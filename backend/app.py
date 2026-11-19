import os
import threading
import time
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from db import get_conn, init_db, DB_PATH
from predictor import predict_match
from scouting import find_scouting_targets

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")
CORS(app)

# Tracks whether the DB currently holds live football-data.org data or the
# bundled sample dataset, plus refresh state for the /api/status endpoint.
DATA_STATE = {
    "source": "sample",
    "last_refreshed": None,
    "refreshing": False,
    "error": None,
}

# Seed the DB on import so this works under gunicorn too (gunicorn imports
# the module directly and never runs the `if __name__ == "__main__"` block).
init_db()


def row_to_dict(row):
    return {k: row[k] for k in row.keys()}


def get_all_players_with_team():
    conn = get_conn()
    rows = conn.execute(
        """SELECT p.*, t.name as team_name, t.league as league
           FROM players p JOIN teams t ON p.team_id = t.id"""
    ).fetchall()
    conn.close()
    return [row_to_dict(r) for r in rows]


@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/api/status")
def api_status():
    return jsonify({
        "data_source": DATA_STATE["source"],
        "last_refreshed": DATA_STATE["last_refreshed"],
        "refreshing": DATA_STATE["refreshing"],
        "error": DATA_STATE["error"],
        "live_available": bool(os.environ.get("FOOTBALL_DATA_API_KEY")),
    })


def _run_live_refresh():
    from fetch_live import build_database

    DATA_STATE["refreshing"] = True
    DATA_STATE["error"] = None
    try:
        key = os.environ["FOOTBALL_DATA_API_KEY"]
        build_database(key)
        DATA_STATE["source"] = "live"
        DATA_STATE["last_refreshed"] = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
    except Exception as exc:  # noqa: BLE001 - surface any failure to the UI
        DATA_STATE["error"] = str(exc)
    finally:
        DATA_STATE["refreshing"] = False


@app.route("/api/refresh-live", methods=["POST"])
def api_refresh_live():
    if not os.environ.get("FOOTBALL_DATA_API_KEY"):
        return jsonify({
            "error": "No FOOTBALL_DATA_API_KEY set on the server. "
                     "Get a free key at https://www.football-data.org/client/register "
                     "and set it as an environment variable before starting the app."
        }), 400
    if DATA_STATE["refreshing"]:
        return jsonify({"status": "already refreshing"}), 202

    thread = threading.Thread(target=_run_live_refresh, daemon=True)
    thread.start()
    return jsonify({"status": "started"}), 202


@app.route("/api/leagues")
def api_leagues():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM leagues").fetchall()
    conn.close()
    return jsonify([row_to_dict(r) for r in rows])


@app.route("/api/teams")
def api_teams():
    league = request.args.get("league")
    conn = get_conn()
    if league:
        rows = conn.execute("SELECT * FROM teams WHERE league = ? ORDER BY name", (league,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM teams ORDER BY name").fetchall()
    conn.close()
    return jsonify([row_to_dict(r) for r in rows])


@app.route("/api/players")
def api_players():
    league = request.args.get("league")
    team_id = request.args.get("team")
    position = request.args.get("position")
    search = request.args.get("search")

    query = """SELECT p.*, t.name as team_name, t.league as league
               FROM players p JOIN teams t ON p.team_id = t.id WHERE 1=1"""
    params = []
    if league:
        query += " AND t.league = ?"
        params.append(league)
    if team_id:
        query += " AND p.team_id = ?"
        params.append(team_id)
    if position:
        query += " AND p.position = ?"
        params.append(position)
    if search:
        query += " AND p.name LIKE ?"
        params.append(f"%{search}%")
    query += " ORDER BY p.goals DESC"

    conn = get_conn()
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return jsonify([row_to_dict(r) for r in rows])


@app.route("/api/player/<int:player_id>")
def api_player(player_id):
    conn = get_conn()
    row = conn.execute(
        """SELECT p.*, t.name as team_name, t.league as league
           FROM players p JOIN teams t ON p.team_id = t.id WHERE p.id = ?""",
        (player_id,),
    ).fetchone()
    conn.close()
    if not row:
        return jsonify({"error": "player not found"}), 404
    return jsonify(row_to_dict(row))


@app.route("/api/compare")
def api_compare():
    p1_id = request.args.get("p1")
    p2_id = request.args.get("p2")
    if not p1_id or not p2_id:
        return jsonify({"error": "p1 and p2 query params are required"}), 400

    conn = get_conn()
    q = """SELECT p.*, t.name as team_name, t.league as league
           FROM players p JOIN teams t ON p.team_id = t.id WHERE p.id = ?"""
    p1 = conn.execute(q, (p1_id,)).fetchone()
    p2 = conn.execute(q, (p2_id,)).fetchone()
    conn.close()
    if not p1 or not p2:
        return jsonify({"error": "one or both players not found"}), 404

    p1, p2 = row_to_dict(p1), row_to_dict(p2)

    def per90(v, m):
        return round(v * 90 / m, 2) if m else 0

    stats = ["goals", "assists", "shots", "shots_on_target", "key_passes", "xg", "xa", "dribbles", "tackles"]
    comparison = []
    for s in stats:
        v1, v2 = per90(p1[s], p1["minutes"]), per90(p2[s], p2["minutes"])
        comparison.append({
            "stat": s,
            "player1_per90": v1,
            "player2_per90": v2,
            "player1_total": p1[s],
            "player2_total": p2[s],
            "edge": p1["name"] if v1 > v2 else (p2["name"] if v2 > v1 else "even"),
        })

    return jsonify({"player1": p1, "player2": p2, "comparison": comparison})


@app.route("/api/predict")
def api_predict():
    team1_id = request.args.get("team1")
    team2_id = request.args.get("team2")
    if not team1_id or not team2_id:
        return jsonify({"error": "team1 and team2 query params are required"}), 400

    conn = get_conn()
    team1 = conn.execute("SELECT * FROM teams WHERE id = ?", (team1_id,)).fetchone()
    team2 = conn.execute("SELECT * FROM teams WHERE id = ?", (team2_id,)).fetchone()
    all_teams = conn.execute("SELECT * FROM teams").fetchall()
    conn.close()

    if not team1 or not team2:
        return jsonify({"error": "one or both teams not found"}), 404

    total_gf = sum(t["goals_for"] for t in all_teams)
    total_played = sum(t["played"] for t in all_teams)
    league_avg_gf = total_gf / total_played
    league_avg_ga = league_avg_gf  # goals for == goals against league-wide

    result = predict_match(row_to_dict(team1), row_to_dict(team2), league_avg_gf, league_avg_ga, neutral=True)
    result["team1"] = row_to_dict(team1)
    result["team2"] = row_to_dict(team2)
    return jsonify(result)


@app.route("/api/scouting")
def api_scouting():
    club_id = request.args.get("club")
    position = request.args.get("position")
    budget = request.args.get("budget")
    budget_m = float(budget) if budget else None

    conn = get_conn()
    club_row = conn.execute("SELECT * FROM teams WHERE id = ?", (club_id,)).fetchone() if club_id else None
    conn.close()
    if club_id and not club_row:
        return jsonify({"error": "club not found"}), 404

    club_name = club_row["name"] if club_row else None
    if budget_m is None and club_row:
        budget_m = club_row["budget_m"]

    players = get_all_players_with_team()
    targets = find_scouting_targets(players, club_name, position, budget_m)
    return jsonify({
        "club": row_to_dict(club_row) if club_row else None,
        "position": position,
        "budget_m": budget_m,
        "targets": targets,
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)
