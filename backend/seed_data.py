"""
Seed data for the Soccer Analytics App.

Covers the top 5 European leagues + the Champions League:
- Premier League (England)
- La Liga (Spain)
- Serie A (Italy)
- Bundesliga* (kept out per spec -> replaced by Ligue 1 per user request)
- Ligue 1 (France)
- UEFA Champions League

NOTE: This is representative sample data (season-aggregate style stats)
built for demo/analysis purposes so the app is fully functional offline
without requiring a paid API key. The data model mirrors what you'd get
from a real provider (e.g. football-data.org / API-FOOTBALL), so swapping
in a live feed later only requires replacing `seed_data.py`'s inserts with
API calls in `fetch_live.py`.
"""

LEAGUES = [
    {"id": "PL", "name": "Premier League", "country": "England"},
    {"id": "PD", "name": "La Liga", "country": "Spain"},
    {"id": "SA", "name": "Serie A", "country": "Italy"},
    {"id": "L1", "name": "Ligue 1", "country": "France"},
    {"id": "UCL", "name": "UEFA Champions League", "country": "Europe"},
]

TEAMS = [
    # Premier League
    {"id": 1, "name": "Manchester City", "league": "PL", "goals_for": 78, "goals_against": 32, "played": 30},
    {"id": 2, "name": "Arsenal", "league": "PL", "goals_for": 71, "goals_against": 28, "played": 30},
    {"id": 3, "name": "Liverpool", "league": "PL", "goals_for": 74, "goals_against": 30, "played": 30},
    {"id": 4, "name": "Manchester United", "league": "PL", "goals_for": 52, "goals_against": 45, "played": 30},
    {"id": 5, "name": "Chelsea", "league": "PL", "goals_for": 58, "goals_against": 42, "played": 30},
    {"id": 6, "name": "Tottenham Hotspur", "league": "PL", "goals_for": 63, "goals_against": 48, "played": 30},
    # La Liga
    {"id": 7, "name": "Real Madrid", "league": "PD", "goals_for": 80, "goals_against": 25, "played": 30},
    {"id": 8, "name": "Barcelona", "league": "PD", "goals_for": 76, "goals_against": 29, "played": 30},
    {"id": 9, "name": "Atletico Madrid", "league": "PD", "goals_for": 62, "goals_against": 30, "played": 30},
    {"id": 10, "name": "Girona", "league": "PD", "goals_for": 55, "goals_against": 38, "played": 30},
    {"id": 11, "name": "Athletic Bilbao", "league": "PD", "goals_for": 50, "goals_against": 33, "played": 30},
    # Serie A
    {"id": 12, "name": "Inter Milan", "league": "SA", "goals_for": 75, "goals_against": 24, "played": 30},
    {"id": 13, "name": "Juventus", "league": "SA", "goals_for": 58, "goals_against": 28, "played": 30},
    {"id": 14, "name": "AC Milan", "league": "SA", "goals_for": 63, "goals_against": 35, "played": 30},
    {"id": 15, "name": "Napoli", "league": "SA", "goals_for": 56, "goals_against": 40, "played": 30},
    {"id": 16, "name": "AS Roma", "league": "SA", "goals_for": 54, "goals_against": 39, "played": 30},
    # Ligue 1
    {"id": 17, "name": "Paris Saint-Germain", "league": "L1", "goals_for": 81, "goals_against": 26, "played": 30},
    {"id": 18, "name": "Monaco", "league": "L1", "goals_for": 60, "goals_against": 34, "played": 30},
    {"id": 19, "name": "Lille", "league": "L1", "goals_for": 52, "goals_against": 33, "played": 30},
    {"id": 20, "name": "Marseille", "league": "L1", "goals_for": 57, "goals_against": 41, "played": 30},
    {"id": 21, "name": "Lyon", "league": "L1", "goals_for": 49, "goals_against": 44, "played": 30},
]

# Players: (name, team_id, position, apps, minutes, goals, assists, shots, shots_on_target,
#           key_passes, xg, xa, pass_accuracy, dribbles, tackles, market_value_m)
PLAYERS = [
    ("Erling Haaland", 1, "FW", 29, 2450, 27, 5, 118, 68, 12, 25.4, 4.8, 78.2, 22, 8, 180),
    ("Kevin De Bruyne", 1, "MF", 22, 1780, 4, 16, 44, 20, 88, 3.9, 12.1, 89.5, 30, 20, 70),
    ("Phil Foden", 1, "MF", 30, 2500, 17, 8, 79, 40, 55, 12.8, 6.9, 87.0, 65, 24, 130),
    ("Bukayo Saka", 2, "FW", 30, 2600, 15, 11, 92, 45, 61, 13.1, 8.4, 84.3, 88, 22, 140),
    ("Martin Odegaard", 2, "MF", 29, 2400, 8, 9, 61, 28, 70, 6.5, 7.8, 90.1, 40, 30, 90),
    ("Declan Rice", 2, "MF", 30, 2650, 6, 5, 35, 14, 40, 4.0, 4.2, 91.4, 20, 55, 110),
    ("Mohamed Salah", 3, "FW", 29, 2480, 22, 12, 110, 58, 66, 21.0, 9.7, 80.5, 70, 15, 100),
    ("Virgil van Dijk", 3, "DF", 28, 2500, 3, 1, 20, 10, 8, 2.1, 0.8, 92.0, 5, 45, 55),
    ("Alexis Mac Allister", 3, "MF", 27, 2200, 5, 6, 38, 16, 45, 4.8, 5.1, 88.9, 25, 40, 65),
    ("Bruno Fernandes", 4, "MF", 30, 2650, 10, 8, 82, 33, 68, 9.9, 7.2, 82.0, 33, 35, 75),
    ("Marcus Rashford", 4, "FW", 29, 2400, 8, 5, 70, 32, 40, 8.7, 4.5, 78.6, 55, 12, 70),
    ("Cole Palmer", 5, "FW", 30, 2600, 20, 10, 100, 52, 60, 15.6, 8.0, 83.1, 60, 18, 120),
    ("Son Heung-min", 6, "FW", 29, 2500, 16, 9, 89, 45, 55, 14.2, 6.8, 81.0, 45, 20, 90),
    ("James Maddison", 6, "MF", 26, 2100, 7, 9, 55, 22, 63, 6.2, 7.5, 84.0, 35, 18, 65),
    ("Jude Bellingham", 7, "MF", 28, 2300, 19, 7, 75, 38, 50, 16.0, 6.1, 88.0, 40, 28, 180),
    ("Vinicius Jr", 7, "FW", 29, 2450, 21, 11, 105, 55, 58, 19.8, 8.9, 82.4, 95, 16, 200),
    ("Kylian Mbappe", 17, "FW", 27, 2300, 26, 6, 120, 65, 45, 24.9, 5.2, 81.0, 80, 10, 180),
    ("Rodrygo", 7, "FW", 28, 2200, 12, 8, 68, 33, 44, 10.9, 6.4, 83.5, 60, 14, 100),
    ("Robert Lewandowski", 8, "FW", 29, 2500, 24, 7, 115, 62, 40, 22.3, 5.9, 79.8, 30, 8, 65),
    ("Pedri", 8, "MF", 26, 2100, 4, 8, 40, 16, 60, 4.5, 7.0, 91.0, 45, 25, 90),
    ("Frenkie de Jong", 8, "MF", 25, 2050, 3, 5, 33, 13, 42, 3.2, 4.9, 92.5, 38, 32, 70),
    ("Antoine Griezmann", 9, "FW", 30, 2600, 15, 12, 85, 41, 65, 12.5, 9.8, 85.0, 40, 22, 45),
    ("Artem Dovbyk", 10, "FW", 30, 2500, 19, 4, 82, 44, 20, 15.8, 3.1, 76.0, 25, 10, 30),
    ("Nico Williams", 11, "FW", 29, 2350, 9, 10, 60, 28, 55, 8.4, 8.7, 82.0, 90, 15, 80),
    ("Lautaro Martinez", 12, "FW", 29, 2480, 25, 6, 108, 60, 35, 21.5, 5.0, 80.0, 35, 12, 110),
    ("Marcus Thuram", 12, "FW", 28, 2400, 14, 9, 70, 35, 48, 12.0, 7.2, 81.5, 45, 14, 75),
    ("Nicolo Barella", 12, "MF", 30, 2600, 6, 7, 45, 18, 55, 5.1, 6.5, 87.0, 30, 40, 65),
    ("Dusan Vlahovic", 13, "FW", 28, 2300, 17, 3, 90, 46, 22, 16.9, 2.4, 77.0, 25, 8, 60),
    ("Federico Chiesa", 13, "FW", 26, 2000, 10, 7, 65, 30, 44, 9.8, 6.0, 80.0, 55, 12, 55),
    ("Rafael Leao", 14, "FW", 29, 2350, 13, 10, 78, 36, 58, 12.2, 8.1, 79.5, 85, 14, 90),
    ("Mike Maignan", 14, "GK", 30, 2700, 0, 0, 0, 0, 2, 0.0, 0.1, 90.0, 2, 5, 45),
    ("Victor Osimhen", 15, "FW", 24, 2100, 18, 4, 85, 48, 25, 17.0, 3.0, 76.5, 30, 8, 120),
    ("Paulo Dybala", 16, "FW", 27, 2000, 12, 9, 60, 28, 50, 10.5, 7.6, 84.0, 65, 12, 40),
    ("Ousmane Dembele", 17, "FW", 28, 2200, 11, 12, 72, 32, 62, 11.2, 9.5, 82.0, 75, 15, 60),
    ("Warren Zaire-Emery", 17, "MF", 22, 2050, 3, 5, 30, 12, 40, 3.0, 5.0, 88.0, 25, 30, 70),
    ("Folarin Balogun", 18, "FW", 29, 2300, 15, 4, 70, 34, 25, 13.0, 3.2, 78.0, 30, 10, 40),
    ("Jonathan David", 19, "FW", 30, 2500, 20, 5, 90, 45, 30, 17.5, 3.8, 79.0, 35, 10, 55),
    ("Pierre-Emerick Aubameyang", 20, "FW", 28, 2350, 19, 4, 82, 44, 22, 16.0, 3.0, 77.5, 25, 8, 25),
    ("Alexandre Lacazette", 21, "FW", 30, 2400, 14, 6, 68, 32, 35, 12.0, 4.8, 80.0, 30, 10, 20),
]

# Approximate market value (in millions) per club, used for scouting budget matching
CLUB_BUDGET = {
    "Manchester City": 200, "Arsenal": 150, "Liverpool": 160, "Manchester United": 140,
    "Chelsea": 180, "Tottenham Hotspur": 110, "Real Madrid": 220, "Barcelona": 150,
    "Atletico Madrid": 100, "Girona": 40, "Athletic Bilbao": 50, "Inter Milan": 90,
    "Juventus": 100, "AC Milan": 90, "Napoli": 80, "AS Roma": 70,
    "Paris Saint-Germain": 200, "Monaco": 60, "Lille": 40, "Marseille": 55, "Lyon": 45,
}
