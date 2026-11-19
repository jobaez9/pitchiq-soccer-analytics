const API = "";
let allPlayers = [];
let allTeams = [];
let allLeagues = [];
let statsChart, compareChart, predictChart;

// ---------- Hero landing animation ----------
function spawnHeroParticles() {
  const wrap = document.getElementById("heroParticles");
  if (!wrap) return;
  const count = 26;
  for (let i = 0; i < count; i++) {
    const p = document.createElement("span");
    p.className = "particle";
    const left = Math.random() * 100;
    const delay = Math.random() * 16;
    const duration = 10 + Math.random() * 10;
    const size = 2 + Math.random() * 3;
    p.style.left = `${left}%`;
    p.style.bottom = `-10px`;
    p.style.width = `${size}px`;
    p.style.height = `${size}px`;
    p.style.animationDelay = `${delay}s`;
    p.style.animationDuration = `${duration}s`;
    wrap.appendChild(p);
  }
}

function animateCount(el, target, duration = 1400) {
  const start = performance.now();
  function tick(now) {
    const progress = Math.min((now - start) / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    el.textContent = Math.round(eased * target);
    if (progress < 1) requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
}

function initHeroCounters() {
  document.querySelectorAll(".hero-stat-value").forEach(el => {
    const target = parseInt(el.dataset.target, 10) || 0;
    animateCount(el, target);
  });
}

function enterDashboard() {
  document.getElementById("appShell").scrollIntoView({ behavior: "smooth" });
}

function initHero() {
  spawnHeroParticles();
  initHeroCounters();
  const enterBtn = document.getElementById("enterAppBtn");
  const scrollCue = document.getElementById("scrollCue");
  if (enterBtn) enterBtn.addEventListener("click", enterDashboard);
  if (scrollCue) scrollCue.addEventListener("click", enterDashboard);
}

// ---------- Tabs ----------
document.querySelectorAll(".tab-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
    document.querySelectorAll(".tab-panel").forEach(p => p.classList.remove("active"));
    btn.classList.add("active");
    document.getElementById(btn.dataset.tab).classList.add("active");
  });
});

async function fetchJSON(url, options) {
  const res = await fetch(url, options);
  if (!res.ok) throw new Error(`Request failed: ${url}`);
  return res.json();
}

// ---------- Data source badge ----------
async function refreshStatusBadge() {
  const badge = document.getElementById("dataSourceBadge");
  const text = document.getElementById("dataSourceText");
  const btn = document.getElementById("refreshLiveBtn");
  try {
    const status = await fetchJSON("/api/status");
    badge.classList.remove("live", "error");
    if (status.error) {
      badge.classList.add("error");
      text.textContent = `Live refresh failed: ${status.error}`;
    } else if (status.refreshing) {
      text.textContent = "Refreshing live data from football-data.org…";
    } else if (status.data_source === "live") {
      badge.classList.add("live");
      text.textContent = `Live data · updated ${status.last_refreshed}`;
    } else {
      text.textContent = status.live_available
        ? "Sample data (click Refresh Live to pull real stats)"
        : "Sample data (set FOOTBALL_DATA_API_KEY on server for live data)";
    }
    btn.disabled = status.refreshing;
    return status;
  } catch (e) {
    text.textContent = "Unable to reach API";
  }
}

async function triggerLiveRefresh() {
  const btn = document.getElementById("refreshLiveBtn");
  btn.disabled = true;
  try {
    const res = await fetch("/api/refresh-live", { method: "POST" });
    const body = await res.json();
    if (!res.ok) {
      alert(body.error || "Could not start live refresh.");
      btn.disabled = false;
      return;
    }
    // Poll status until refresh completes, then reload data.
    const poll = setInterval(async () => {
      const status = await refreshStatusBadge();
      if (status && !status.refreshing) {
        clearInterval(poll);
        if (status.data_source === "live" && !status.error) {
          await init(); // reload all datasets + re-render current views
        }
      }
    }, 2000);
  } catch (e) {
    alert("Network error starting live refresh.");
    btn.disabled = false;
  }
}

// ---------- Init ----------
let listenersBound = false;

async function init() {
  [allLeagues, allTeams, allPlayers] = await Promise.all([
    fetchJSON("/api/leagues"),
    fetchJSON("/api/teams"),
    fetchJSON("/api/players"),
  ]);

  populateLeagueSelect(document.getElementById("statsLeague"));
  populatePlayerSelects();
  populateTeamSelects();
  populateClubSelect();

  renderStats();

  if (!listenersBound) {
    document.getElementById("statsLeague").addEventListener("change", renderStats);
    document.getElementById("statsPosition").addEventListener("change", renderStats);
    document.getElementById("statsSearch").addEventListener("input", renderStats);

    document.getElementById("compareBtn").addEventListener("click", renderCompare);
    document.getElementById("predictBtn").addEventListener("click", renderPredict);
    document.getElementById("scoutBtn").addEventListener("click", renderScouting);
    document.getElementById("refreshLiveBtn").addEventListener("click", triggerLiveRefresh);
    listenersBound = true;
  }
}

function populateLeagueSelect(select) {
  select.innerHTML = '<option value="">All Leagues</option>';
  allLeagues.forEach(l => {
    const opt = document.createElement("option");
    opt.value = l.id;
    opt.textContent = l.name;
    select.appendChild(opt);
  });
}

function populatePlayerSelects() {
  const p1 = document.getElementById("p1Select");
  const p2 = document.getElementById("p2Select");
  p1.innerHTML = "";
  p2.innerHTML = "";
  const sorted = [...allPlayers].sort((a, b) => a.name.localeCompare(b.name));
  sorted.forEach(p => {
    [p1, p2].forEach(sel => {
      const opt = document.createElement("option");
      opt.value = p.id;
      opt.textContent = `${p.name} (${p.team_name})`;
      sel.appendChild(opt.cloneNode(true));
    });
  });
  if (sorted.length > 1) {
    p1.value = sorted[0].id;
    p2.value = sorted[1].id;
  }
}

function populateTeamSelects() {
  const t1 = document.getElementById("team1Select");
  const t2 = document.getElementById("team2Select");
  t1.innerHTML = "";
  t2.innerHTML = "";
  const sorted = [...allTeams].sort((a, b) => a.name.localeCompare(b.name));
  sorted.forEach(t => {
    [t1, t2].forEach(sel => {
      const opt = document.createElement("option");
      opt.value = t.id;
      opt.textContent = `${t.name} (${t.league})`;
      sel.appendChild(opt.cloneNode(true));
    });
  });
  if (sorted.length > 1) {
    t1.value = sorted[0].id;
    t2.value = sorted[1].id;
  }
}

function populateClubSelect() {
  const sel = document.getElementById("scoutClub");
  sel.innerHTML = "";
  const sorted = [...allTeams].sort((a, b) => a.name.localeCompare(b.name));
  sorted.forEach(t => {
    const opt = document.createElement("option");
    opt.value = t.id;
    opt.textContent = `${t.name} (${t.league})`;
    sel.appendChild(opt);
  });
}

// ---------- Stats Tab ----------
async function renderStats() {
  const league = document.getElementById("statsLeague").value;
  const position = document.getElementById("statsPosition").value;
  const search = document.getElementById("statsSearch").value;

  const params = new URLSearchParams();
  if (league) params.set("league", league);
  if (position) params.set("position", position);
  if (search) params.set("search", search);

  const players = await fetchJSON(`/api/players?${params.toString()}`);
  const top = players.slice(0, 15);

  const ctx = document.getElementById("statsChart");
  const data = {
    labels: top.map(p => p.name),
    datasets: [
      { label: "Shots on Target", data: top.map(p => p.shots_on_target), backgroundColor: "#35d0ba" },
      { label: "Assists", data: top.map(p => p.assists), backgroundColor: "#7c8cff" },
    ],
  };
  if (statsChart) statsChart.destroy();
  statsChart = new Chart(ctx, {
    type: "bar",
    data,
    options: {
      responsive: true,
      plugins: { legend: { labels: { color: "#e9edf7" } } },
      scales: {
        x: { ticks: { color: "#93a0c4", maxRotation: 60, minRotation: 40 }, grid: { color: "rgba(255,255,255,.05)" } },
        y: { ticks: { color: "#93a0c4" }, grid: { color: "rgba(255,255,255,.05)" } },
      },
    },
  });

  const tbody = document.querySelector("#statsTable tbody");
  tbody.innerHTML = players.map(p => `
    <tr>
      <td>${p.name}</td><td>${p.team_name}</td><td>${p.position}</td>
      <td>${p.goals}</td><td>${p.assists}</td><td>${p.shots}</td>
      <td>${p.shots_on_target}</td><td>${p.xg.toFixed(1)}</td>
    </tr>`).join("");
}

// ---------- Compare Tab ----------
async function renderCompare() {
  const p1 = document.getElementById("p1Select").value;
  const p2 = document.getElementById("p2Select").value;
  if (!p1 || !p2) return;
  const result = await fetchJSON(`/api/compare?p1=${p1}&p2=${p2}`);

  document.getElementById("p1Header").textContent = result.player1.name;
  document.getElementById("p2Header").textContent = result.player2.name;

  const labels = result.comparison.map(c => c.stat.replace(/_/g, " "));
  const ctx = document.getElementById("compareChart");
  if (compareChart) compareChart.destroy();
  compareChart = new Chart(ctx, {
    type: "radar",
    data: {
      labels,
      datasets: [
        { label: result.player1.name, data: result.comparison.map(c => c.player1_per90), backgroundColor: "rgba(53,208,186,.25)", borderColor: "#35d0ba" },
        { label: result.player2.name, data: result.comparison.map(c => c.player2_per90), backgroundColor: "rgba(124,140,255,.25)", borderColor: "#7c8cff" },
      ],
    },
    options: {
      responsive: true,
      plugins: { legend: { labels: { color: "#e9edf7" } } },
      scales: {
        r: {
          angleLines: { color: "rgba(255,255,255,.1)" },
          grid: { color: "rgba(255,255,255,.1)" },
          pointLabels: { color: "#93a0c4", font: { size: 11 } },
          ticks: { color: "#93a0c4", backdropColor: "transparent" },
        },
      },
    },
  });

  const tbody = document.querySelector("#compareTable tbody");
  tbody.innerHTML = result.comparison.map(c => `
    <tr>
      <td>${c.stat.replace(/_/g, " ")}</td>
      <td>${c.player1_per90} <span style="color:#93a0c4">(${c.player1_total})</span></td>
      <td>${c.player2_per90} <span style="color:#93a0c4">(${c.player2_total})</span></td>
      <td>${c.edge}</td>
    </tr>`).join("");
}

// ---------- Predict Tab ----------
async function renderPredict() {
  const team1 = document.getElementById("team1Select").value;
  const team2 = document.getElementById("team2Select").value;
  if (!team1 || !team2) return;
  const result = await fetchJSON(`/api/predict?team1=${team1}&team2=${team2}`);

  const ctx = document.getElementById("predictChart");
  if (predictChart) predictChart.destroy();
  predictChart = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: [`${result.team1.name} Win`, "Draw", `${result.team2.name} Win`],
      datasets: [{
        data: [result.team1_win_pct, result.draw_pct, result.team2_win_pct],
        backgroundColor: ["#35d0ba", "#ffcc66", "#ff6b81"],
        borderWidth: 0,
      }],
    },
    options: {
      responsive: true,
      plugins: { legend: { position: "bottom", labels: { color: "#e9edf7" } } },
    },
  });

  document.getElementById("predictSummary").innerHTML = `
    <div class="stat-box"><div class="label">${result.team1.name} xG</div><div class="value">${result.team1_expected_goals}</div></div>
    <div class="stat-box"><div class="label">${result.team2.name} xG</div><div class="value">${result.team2_expected_goals}</div></div>
    <div class="stat-box"><div class="label">Most Likely Winner</div><div class="value">${
      result.team1_win_pct > result.team2_win_pct && result.team1_win_pct > result.draw_pct ? result.team1.name :
      result.team2_win_pct > result.draw_pct ? result.team2.name : "Draw"
    }</div></div>
  `;

  const tbody = document.querySelector("#scorelineTable tbody");
  tbody.innerHTML = result.most_likely_scorelines.map(s => `
    <tr><td>${s.score}</td><td>${s.probability_pct}%</td></tr>
  `).join("");
}

// ---------- Scouting Tab ----------
async function renderScouting() {
  const club = document.getElementById("scoutClub").value;
  const position = document.getElementById("scoutPosition").value;
  const budget = document.getElementById("scoutBudget").value;

  const params = new URLSearchParams();
  if (club) params.set("club", club);
  if (position) params.set("position", position);
  if (budget) params.set("budget", budget);

  const result = await fetchJSON(`/api/scouting?${params.toString()}`);
  const tbody = document.querySelector("#scoutTable tbody");
  tbody.innerHTML = result.targets.map((t, i) => `
    <tr>
      <td>${i + 1}</td>
      <td>${t.name}</td>
      <td>${t.team_name}</td>
      <td>${t.league}</td>
      <td>${t.position}</td>
      <td>${t.fit_score}</td>
      <td>€${t.market_value_m}</td>
      <td>${t.fits_budget ? '<span class="badge-yes">Yes</span>' : '<span class="badge-no">No</span>'}</td>
    </tr>`).join("");
}

initHero();
init();
refreshStatusBadge();
