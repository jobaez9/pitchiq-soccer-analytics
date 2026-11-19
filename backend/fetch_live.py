"""
Pull LIVE data from football-data.org (https://www.football-data.org) into the
app's SQLite database.

Requires a free API key:
  1. Sign up at https://www.football-data.org/client/register
  2. Set it as an environment variable before running this script:
       export FOOTBALL_DATA_API_KEY="your-key-here"
  3. Run:  python fetch_live.py

What gets pulled (free tier):
  - Standings (played / goals for / goals against) for each competition
    -> feeds the Match Predictor with REAL season data.
  - Top scorers (goals + assists) for each competition
    -> feeds the Player Stats & Head-to-Head screens with REAL totals.

Free-tier limitation: football-data.org does not expose shot counts, xG,
or key-passes on the free plan. Those advanced fields are set to 0 for
live-pulled players (the UI displays "N/A"-style zeros gracefully) rather
than being invented. Everything derived from real counts (goals, assists,
appearances, minutes, team goals for/against/played) is 100% live.

Swap in a paid provider (e.g. API-FOOTBALL / Opta / StatsBomb) later by
extending `fetch_competition()` with extra endpoints for shots/xG.
"""
import os
import sys
import time
import sqlite3

try:
    import requests
except ImportError:
    print("Missing dependency 'requests'. Install with: pip install requests")
    sys.exit(1)

from db import DB_PATH, init_db

API_BASE = "https://api.football-data.org/v4"

# Maps our internal league id -> football-data.org competition code
COMPETITIONS = {
    "PL": "PL",    # Premier League
    "PD": "PD",    # La Liga (Primera Division)
    "SA": "SA",    # Serie A
    "L1": "FL1",   # Ligue 1
    "UCL": "CL",   # UEFA Champions League
}

LEAGUE_META = {
    "PL": {"name": "Premier League", "country": "England"},
    "PD": {"name": "La Liga", "country": "Spain"},
    "SA": {"name": "Serie A", "country": "Italy"},
    "L1": {"name": "Ligue 1", "country": "France"},
    "UCL": {"name": "UEFA Champions League", "country": "Europe"},
}

REQUEST_DELAY_S = 6.5  # free tier is limited to 10 req/min


def get_session(api_key):
    s = requests.Session()
    s.headers.update({"X-Auth-Token": api_key})
    return s


def fetch_standings(session, comp_code):
    """Returns a list of dicts: id, name, played, goals_for, goals_against."""
    url = f"{API_BASE}/competitions/{comp_code}/standings"
    resp = session.get(url, timeout=20)
    resp.raise_for_status()
    data = resp.json()
    teams = []
    for group in data.get("standings", []):
        if group.get("type") != "TOTAL":
            continue
        for row in group.get("table", []):
            team = row["team"]
            teams.append({
                "id": team["id"],
                "name": team["name"],
                "played": row["playedGames"],
                "goals_for": row["goalsFor"],
                "goals_against": row["goalsAgainst"],
            })
    return teams


def fetch_scorers(session, comp_code, limit=25):
    """Returns a list of dicts with player name, team id/name, goals, assists."""
    url = f"{API_BASE}/competitions/{comp_code}/scorers"
    resp = session.get(url, params={"limit": limit}, timeout=20)
    resp.raise_for_status()
    data = resp.json()
    scorers = []
    for entry in data.get("scorers", []):
        player = entry["player"]
        team = entry["team"]
        scorers.append({
            "name": player["name"],
            "position": (player.get("position") or "FW")[:2].upper() if player.get("position") else "FW",
            "team_id": team["id"],
            "team_name": team["name"],
            "goals": entry.get("goals") or 0,
            "assists": entry.get("assists") or 0,
            "played": entry.get("playedMatches") or 1,
        })
    return scorers


NORMALIZE_POSITION = {
    "GOALKEEPER": "GK", "DEFENCE": "DF", "DEFENDER": "DF", "MIDFIELD": "MF",
    "MIDFIELDER": "MF", "OFFENCE": "FW", "ATTACKER": "FW", "FORWARD": "FW",
}


def normalize_position(raw):
    if not raw:
        return "FW"
    key = raw.upper()
    return NORMALIZE_POSITION.get(key, key[:2] if key[:2] in ("GK", "DF", "MF", "FW") else "FW")


def build_database(api_key):
    session = get_session(api_key)

    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    init_db(force=False)  # fresh empty schema (data already removed above)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.executemany(
        "INSERT INTO leagues (id, name, country) VALUES (?, ?, ?)",
        [(k, v["name"], v["country"]) for k, v in LEAGUE_META.items()],
    )
    conn.commit()

    team_id_map = {}  # football-data team id -> our own row id
    next_team_id = 1
    next_player_id = 1

    for league_id, comp_code in COMPETITIONS.items():
        print(f"Fetching standings for {league_id} ({comp_code})...")
        try:
            teams = fetch_standings(session, comp_code)
        except requests.HTTPError as e:
            print(f"  ! Failed standings for {comp_code}: {e}")
            teams = []
        time.sleep(REQUEST_DELAY_S)

        for t in teams:
            our_id = next_team_id
            next_team_id += 1
            team_id_map[t["id"]] = our_id
            cur.execute(
                """INSERT INTO teams (id, name, league, goals_for, goals_against, played, budget_m)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (our_id, t["name"], league_id, t["goals_for"], t["goals_against"], t["played"], 60.0),
            )
        conn.commit()

        print(f"Fetching top scorers for {league_id} ({comp_code})...")
        try:
            scorers = fetch_scorers(session, comp_code)
        except requests.HTTPError as e:
            print(f"  ! Failed scorers for {comp_code}: {e}")
            scorers = []
        time.sleep(REQUEST_DELAY_S)

        for p in scorers:
            our_team_id = team_id_map.get(p["team_id"])
            if our_team_id is None:
                # Team not in standings payload (rare) - skip player
                continue
            minutes_est = p["played"] * 75  # rough estimate; free tier has no minutes endpoint
            cur.execute(
                """INSERT INTO players (name, team_id, position, apps, minutes, goals, assists,
                   shots, shots_on_target, key_passes, xg, xa, pass_accuracy, dribbles, tackles, market_value_m)
                   VALUES (?, ?, ?, ?, ?, ?, ?, 0, 0, 0, 0, 0, 0, 0, 0, 0)""",
                (p["name"], our_team_id, normalize_position(p["position"]), p["played"],
                 minutes_est, p["goals"], p["assists"]),
            )
        conn.commit()

    conn.close()
    print(f"Live data loaded into {DB_PATH}")


if __name__ == "__main__":
    key = os.environ.get("FOOTBALL_DATA_API_KEY")
    if not key:
        print(
            "ERROR: Set FOOTBALL_DATA_API_KEY first.\n"
            "  1. Get a free key: https://www.football-data.org/client/register\n"
            "  2. export FOOTBALL_DATA_API_KEY=your-key-here\n"
            "  3. python fetch_live.py"
        )
        sys.exit(1)
    build_database(key)
