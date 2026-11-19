"""
Match outcome predictor using a Poisson-distribution goal model.

This is the standard statistical approach used in football analytics
(Maher, 1982; widely used by odds compilers): each team's expected goals
(lambda) for the match is derived from their attacking strength and the
opponent's defensive weakness relative to the league average. Final score
probabilities come from the independent Poisson distributions for each
team's goal count, and match outcome probabilities (win/draw/loss) are
obtained by summing over the score-grid.
"""
import math

HOME_ADVANTAGE = 1.10  # ~10% boost to the "team1" side, mirroring home-field effect


def poisson_pmf(k, lam):
    return (lam ** k) * math.exp(-lam) / math.factorial(k)


def team_strengths(team, league_avg_gf, league_avg_ga):
    played = max(team["played"], 1)
    attack = (team["goals_for"] / played) / league_avg_gf if league_avg_gf else 1
    defense = (team["goals_against"] / played) / league_avg_ga if league_avg_ga else 1
    return attack, defense


def predict_match(team1, team2, league_avg_gf, league_avg_ga, neutral=True, max_goals=8):
    a1, d1 = team_strengths(team1, league_avg_gf, league_avg_ga)
    a2, d2 = team_strengths(team2, league_avg_gf, league_avg_ga)

    lam1 = a1 * d2 * league_avg_gf
    lam2 = a2 * d1 * league_avg_gf

    if not neutral:
        lam1 *= HOME_ADVANTAGE

    # Clamp to sane bounds
    lam1 = max(0.15, min(lam1, 5.5))
    lam2 = max(0.15, min(lam2, 5.5))

    p1_win = p2_win = draw = 0.0
    scoreline_probs = {}
    for g1 in range(max_goals + 1):
        for g2 in range(max_goals + 1):
            p = poisson_pmf(g1, lam1) * poisson_pmf(g2, lam2)
            scoreline_probs[(g1, g2)] = p
            if g1 > g2:
                p1_win += p
            elif g1 < g2:
                p2_win += p
            else:
                draw += p

    top_scorelines = sorted(scoreline_probs.items(), key=lambda x: -x[1])[:5]

    total = p1_win + p2_win + draw
    return {
        "team1_win_pct": round(100 * p1_win / total, 1),
        "draw_pct": round(100 * draw / total, 1),
        "team2_win_pct": round(100 * p2_win / total, 1),
        "team1_expected_goals": round(lam1, 2),
        "team2_expected_goals": round(lam2, 2),
        "most_likely_scorelines": [
            {"score": f"{s[0]}-{s[1]}", "probability_pct": round(100 * p, 1)}
            for s, p in top_scorelines
        ],
    }
