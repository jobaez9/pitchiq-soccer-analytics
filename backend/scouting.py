"""
Scouting engine: given a club and a target position, rank the best-fit
players from across the top 5 leagues + Champions League who are not
already at that club, weighted by position-relevant per-90 production,
and flagged by whether they fit the club's estimated transfer budget.
"""

POSITION_WEIGHTS = {
    "FW": {"goals": 3.0, "assists": 1.5, "xg": 2.0, "xa": 1.0, "shots_on_target": 0.8, "dribbles": 0.3, "key_passes": 0.4, "tackles": 0.05, "pass_accuracy": 0.02},
    "MF": {"goals": 1.2, "assists": 2.2, "xg": 0.8, "xa": 1.8, "shots_on_target": 0.3, "dribbles": 0.4, "key_passes": 1.2, "tackles": 0.5, "pass_accuracy": 0.06},
    "DF": {"goals": 0.6, "assists": 0.8, "xg": 0.3, "xa": 0.4, "shots_on_target": 0.1, "dribbles": 0.1, "key_passes": 0.3, "tackles": 1.8, "pass_accuracy": 0.08},
    "GK": {"goals": 0, "assists": 0, "xg": 0, "xa": 0, "shots_on_target": 0, "dribbles": 0, "key_passes": 0, "tackles": 0.1, "pass_accuracy": 0.1},
}


def per90(value, minutes):
    if not minutes:
        return 0.0
    return value * 90.0 / minutes


def scouting_score(player, position):
    weights = POSITION_WEIGHTS.get(position, POSITION_WEIGHTS["MF"])
    minutes = player["minutes"] or 1
    score = 0.0
    for stat, w in weights.items():
        if stat == "pass_accuracy":
            score += w * (player["pass_accuracy"] or 0)
        else:
            score += w * per90(player[stat] or 0, minutes)
    return round(score, 2)


def find_scouting_targets(players, club_name, position, budget_m=None, top_n=8):
    candidates = [p for p in players if p["team_name"] != club_name]
    if position:
        candidates = [p for p in candidates if p["position"] == position]

    scored = []
    for p in candidates:
        s = scouting_score(p, p["position"])
        fits_budget = budget_m is None or (p["market_value_m"] or 0) <= budget_m
        scored.append({**p, "fit_score": s, "fits_budget": fits_budget})

    scored.sort(key=lambda x: (-x["fits_budget"], -x["fit_score"]))
    return scored[:top_n]
