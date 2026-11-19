"""Database layer: builds an in-memory-backed SQLite file and seeds it."""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "soccer.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(force=False):
    if force and os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    fresh = not os.path.exists(DB_PATH)
    conn = get_conn()
    cur = conn.cursor()
    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS leagues (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            country TEXT
        );
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            league TEXT NOT NULL,
            goals_for INTEGER,
            goals_against INTEGER,
            played INTEGER,
            budget_m REAL,
            FOREIGN KEY(league) REFERENCES leagues(id)
        );
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            team_id INTEGER NOT NULL,
            position TEXT,
            apps INTEGER,
            minutes INTEGER,
            goals INTEGER,
            assists INTEGER,
            shots INTEGER,
            shots_on_target INTEGER,
            key_passes INTEGER,
            xg REAL,
            xa REAL,
            pass_accuracy REAL,
            dribbles INTEGER,
            tackles INTEGER,
            market_value_m REAL,
            FOREIGN KEY(team_id) REFERENCES teams(id)
        );
        """
    )
    conn.commit()

    if fresh:
        from seed_data import LEAGUES, TEAMS, PLAYERS, CLUB_BUDGET

        cur.executemany(
            "INSERT INTO leagues (id, name, country) VALUES (:id, :name, :country)",
            LEAGUES,
        )
        for t in TEAMS:
            cur.execute(
                """INSERT INTO teams (id, name, league, goals_for, goals_against, played, budget_m)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    t["id"], t["name"], t["league"], t["goals_for"], t["goals_against"],
                    t["played"], CLUB_BUDGET.get(t["name"], 40),
                ),
            )
        for p in PLAYERS:
            cur.execute(
                """INSERT INTO players (name, team_id, position, apps, minutes, goals, assists,
                   shots, shots_on_target, key_passes, xg, xa, pass_accuracy, dribbles, tackles, market_value_m)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                p,
            )
        conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db(force=True)
    print("Database initialized at", DB_PATH)
