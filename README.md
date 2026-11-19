# PitchIQ — Soccer Analytics Web App

A full-stack analytics dashboard covering the **top 5 European leagues**
(Premier League, La Liga, Serie A, Ligue 1) plus the **UEFA Champions League**.

## Features
1. **Shots & Assists Explorer** — filter/search players by league/position, view charts + leaderboard.
2. **Head-to-Head Comparison** — compare any two players' per-90 stats on a radar chart.
3. **Match Predictor** — Poisson goal-expectancy model (attack/defense strength vs. league average) estimating win/draw/loss probabilities and likely scorelines.
4. **Scouting Recommender** — ranks the best transfer targets for a club's positional need, weighted by position-specific stats and budget fit.

## Stack
- Backend: Python + Flask + SQLite (`backend/`)
- Frontend: HTML/CSS/vanilla JS + Chart.js (`frontend/`)

## Data
Ships with a realistic **sample dataset** (season-aggregate stats for 21 clubs / 39 players)
so the app works fully offline without needing an API key.

### 🔴 Live data (football-data.org)
The app can pull **real** standings and top-scorer stats from
[football-data.org](https://www.football-data.org):

1. Get a free API key: https://www.football-data.org/client/register
2. Set it as an environment variable before starting the server:
   ```bash
   export FOOTBALL_DATA_API_KEY="your-key-here"
   ```
3. Start the app (`python app.py`), then click **⟳ Refresh Live** in the top bar
   (or run `python fetch_live.py` directly). This replaces the database with
   live standings (played/goals for/against — powers the Match Predictor) and
   live top-scorer goals & assists (powers Player Stats & Head-to-Head).

   **Free-tier limitation:** football-data.org's free plan doesn't expose
   shots, xG, or key-passes, so those fields come back as 0 for live players
   instead of being invented. Swap in a paid provider (API-FOOTBALL, Opta,
   StatsBomb, etc.) by extending `backend/fetch_live.py`.

The top bar shows a live status badge (🟡 sample / 🟢 live) and refresh timestamp.

## Run it

```bash
cd backend
python3 -m venv ../venv        # first time only
source ../venv/bin/activate
pip install flask flask-cors requests
python db.py                   # seed the database with sample data (first time only)
python app.py                  # starts on http://localhost:5050
```

Then open **http://localhost:5050** in your browser.

## Let anyone see it (public sharing)

**Quick/temporary — Cloudflare Tunnel (no account needed):**
```bash
# download once: https://github.com/cloudflare/cloudflared/releases
./cloudflared tunnel --url http://localhost:5050
```
This prints a public `https://<random>.trycloudflare.com` URL that proxies to
your local server. It's great for demos, but the URL changes every time you
restart the tunnel and it only stays up while your machine + server are running.

**Permanent — deploy to a host:** for a stable public URL, deploy the Flask
app to a service like Render, Railway, Fly.io, or PythonAnywhere (all have
free tiers). Point their start command at `python backend/app.py` (bind to
`0.0.0.0` and the platform's `$PORT`), and set `FOOTBALL_DATA_API_KEY` in
their environment variables dashboard for live data.

