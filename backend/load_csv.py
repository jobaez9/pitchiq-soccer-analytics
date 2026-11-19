"""
Load the app's SQLite database from CSV files instead of seed_data.py.

Expected files in backend/data/:
  - leagues.csv : id,name,country
  - teams.csv   : id,name,league,goals_for,goals_against,played,budget_m
  - players.csv : name,team_id,position,apps,minutes,goals,assists,shots,
                  shots_on_target,key_passes,xg,xa,pass_accuracy,dribbles,
                  tackles,market_value_m

Usage:
    python load_csv.py                 # loads backend/data/*.csv, replacing the DB
    python load_csv.py --dir mydata    # loads CSVs from a custom folder
"""
import argparse
import csv
import os
import sqlite3

from db import DB_PATH

REQUIRED_FILES = ["leagues.csv", "teams.csv", "players.csv"]

INT_FIELDS = {
    "teams": ["goals_for", "goals_against", "played"],
    "players": ["team_id", "apps", "minutes", "goals", "assists", "shots",
                "shots_on_target", "key_passes", "dribbles", "tackles"],
}
FLOAT_FIELDS = {
    "teams": ["budget_m"],
    "players": ["xg", "xa", "pass_accuracy", "market_value_m"],
}


def read_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def coerce_row(table, row):
    for field in INT_FIELDS.get(table, []):
        row[field] = int(float(row[field])) if row.get(field) not in (None, "") else 0
    for field in FLOAT_FIELDS.get(table, []):
        row[field] = float(row[field]) if row.get(field) not in (None, "") else 0.0
    return row


def load(data_dir):
    for fname in REQUIRED_FILES:
        fpath = os.path.join(data_dir, fname)
        if not os.path.exists(fpath):
            raise SystemExit(f"Missing required file: {fpath}")

    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    # Recreate empty schema (reuses db.py's CREATE TABLE statements)
    from db import init_db
    init_db(force=False)  # DB was just removed, so this creates fresh empty tables only

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    leagues = read_csv(os.path.join(data_dir, "leagues.csv"))
    cur.executemany(
        "INSERT INTO leagues (id, name, country) VALUES (:id, :name, :country)",
        leagues,
    )

    teams = [coerce_row("teams", r) for r in read_csv(os.path.join(data_dir, "teams.csv"))]
    for t in teams:
        cur.execute(
            """INSERT INTO teams (id, name, league, goals_for, goals_against, played, budget_m)
               VALUES (:id, :name, :league, :goals_for, :goals_against, :played, :budget_m)""",
            t,
        )

    players = [coerce_row("players", r) for r in read_csv(os.path.join(data_dir, "players.csv"))]
    for p in players:
        p.setdefault("id", None)
        cur.execute(
            """INSERT INTO players (name, team_id, position, apps, minutes, goals, assists,
               shots, shots_on_target, key_passes, xg, xa, pass_accuracy, dribbles, tackles, market_value_m)
               VALUES (:name, :team_id, :position, :apps, :minutes, :goals, :assists,
               :shots, :shots_on_target, :key_passes, :xg, :xa, :pass_accuracy, :dribbles, :tackles, :market_value_m)""",
            p,
        )

    conn.commit()
    conn.close()
    print(f"Loaded {len(leagues)} leagues, {len(teams)} teams, {len(players)} players from '{data_dir}' into {DB_PATH}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", default=os.path.join(os.path.dirname(__file__), "data"),
                         help="Folder containing leagues.csv, teams.csv, players.csv")
    args = parser.parse_args()
    load(args.dir)
