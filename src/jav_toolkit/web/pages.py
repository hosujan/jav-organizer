INDEX_HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>JAV Organizer</title>
  <style>
    :root {
      --bg: #f3efe4;
      --panel: #fffaf0;
      --ink: #1f2933;
      --muted: #6b7280;
      --accent: #0f766e;
      --line: #d6d3c7;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: "Avenir Next", "Segoe UI", sans-serif;
      color: var(--ink);
      background: radial-gradient(circle at 10% 10%, #fff8e7 0, var(--bg) 45%, #ece7db 100%);
    }
    .wrap {
      max-width: 1200px;
      margin: 0 auto;
      padding: 24px;
    }
    .panel {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 16px;
      margin-bottom: 16px;
      box-shadow: 0 4px 16px rgba(20, 20, 20, 0.06);
    }
    h1 {
      margin: 0 0 8px;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      font-size: 26px;
    }
    .row {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      align-items: center;
    }
    button, input {
      font: inherit;
      border-radius: 10px;
      border: 1px solid var(--line);
      padding: 10px 12px;
      background: #fff;
    }
    button.primary {
      background: var(--accent);
      color: #fff;
      border-color: var(--accent);
      cursor: pointer;
    }
    .hint { color: var(--muted); font-size: 14px; }
    .logs {
      background: #111827;
      color: #d1fae5;
      font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
      border-radius: 10px;
      padding: 10px;
      height: 180px;
      overflow: auto;
      font-size: 12px;
      white-space: pre-wrap;
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
      gap: 14px;
    }
    .card {
      position: relative;
      border-radius: 12px;
      overflow: hidden;
      border: 1px solid var(--line);
      background: #fff;
      text-decoration: none;
      color: inherit;
      transform: translateY(0);
      transition: transform .18s ease, box-shadow .18s ease;
    }
    .card:hover {
      transform: translateY(-3px);
      box-shadow: 0 8px 20px rgba(15, 118, 110, 0.18);
    }
    .media {
      position: relative;
      aspect-ratio: 2 / 3;
      background: #e5e7eb;
      overflow: hidden;
    }
    .media img, .media video {
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
    }
    .media video {
      position: absolute;
      inset: 0;
      opacity: 0;
      transition: opacity .2s ease;
      pointer-events: none;
    }
    .card:hover .media video { opacity: 1; }
    .meta {
      padding: 10px;
      font-size: 13px;
    }
    .meta .id { font-weight: 700; letter-spacing: .03em; }
    @media (max-width: 680px) {
      .wrap { padding: 14px; }
      h1 { font-size: 22px; }
    }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="panel">
      <h1>JAV Organizer</h1>
      <p class="hint">Choose local folder -> process one by one -> browse and play local videos.</p>
      <div class="row">
        <button id="chooseBtn" class="primary">Choose Local Directory</button>
        <input id="manualPath" type="text" placeholder="Fallback: enter local path manually" style="min-width:320px" />
        <button id="manualBtn">Use Path</button>
        <button id="processBtn" class="primary">Start Processing</button>
      </div>
      <p id="status" class="hint"></p>
    </div>

    <div class="panel">
      <div class="row" style="justify-content:space-between">
        <strong>Progress</strong>
        <span id="progressText" class="hint"></span>
      </div>
      <div id="logs" class="logs"></div>
    </div>

    <div class="panel">
      <strong>Library</strong>
      <div id="grid" class="grid" style="margin-top:12px"></div>
    </div>
  </div>

  <script>
    const statusEl = document.getElementById("status");
    const progressEl = document.getElementById("progressText");
    const logsEl = document.getElementById("logs");
    const gridEl = document.getElementById("grid");
    const chooseBtn = document.getElementById("chooseBtn");
    const processBtn = document.getElementById("processBtn");
    const manualBtn = document.getElementById("manualBtn");
    const manualPath = document.getElementById("manualPath");

    async function post(url, body) {
      const res = await fetch(url, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(body || {})
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.error || res.statusText);
      return data;
    }

    async function get(url) {
      const res = await fetch(url);
      if (!res.ok) throw new Error(res.statusText);
      return res.json();
    }

    async function chooseDir() {
      try {
        const data = await post("/api/select-directory", {});
        statusEl.textContent = "Selected: " + data.selected_dir + " (" + data.count + " matched videos)";
        await refreshState();
      } catch (e) {
        statusEl.textContent = "Choose failed: " + e.message;
      }
    }

    async function chooseManual() {
      const path = manualPath.value.trim();
      if (!path) return;
      try {
        const data = await post("/api/select-directory", {path});
        statusEl.textContent = "Selected: " + data.selected_dir + " (" + data.count + " matched videos)";
        await refreshState();
      } catch (e) {
        statusEl.textContent = "Path failed: " + e.message;
      }
    }

    async function startProcess() {
      try {
        await post("/api/process", {});
        statusEl.textContent = "Processing started.";
      } catch (e) {
        statusEl.textContent = "Start failed: " + e.message;
      }
    }

    function renderLogs(lines) {
      logsEl.textContent = lines.join("\\n");
      logsEl.scrollTop = logsEl.scrollHeight;
    }

    function renderGrid(videos) {
      gridEl.innerHTML = "";
      for (const v of videos) {
        const a = document.createElement("a");
        a.className = "card";
        a.href = "/watch/" + encodeURIComponent(v.jav_id);
        const title = (v.title || "Untitled").replaceAll('"', "&quot;");
        a.innerHTML = `
          <div class="media">
            <img src="${v.poster_url}" alt="${title}" loading="lazy" />
            <video muted loop playsinline preload="none" src="${v.preview_url}"></video>
          </div>
          <div class="meta">
            <div class="id">${v.jav_id}</div>
            <div>${title}</div>
            <div class="hint">${v.release_date || "—"} ${v.publisher || ""}</div>
          </div>
        `;
        const vid = a.querySelector("video");
        a.addEventListener("mouseenter", () => { vid.play().catch(() => {}); });
        a.addEventListener("mouseleave", () => { vid.pause(); vid.currentTime = 0; });
        gridEl.appendChild(a);
      }
    }

    async function refreshState() {
      const state = await get("/api/state");
      const current = state.current ? " current: " + state.current : "";
      progressEl.textContent = state.processed + " / " + state.total + (state.processing ? " (running)" : " (idle)") + current;
      renderLogs(state.logs || []);
      const videos = await get("/api/videos");
      renderGrid(videos);
    }

    chooseBtn.addEventListener("click", chooseDir);
    manualBtn.addEventListener("click", chooseManual);
    processBtn.addEventListener("click", startProcess);

    refreshState();
    setInterval(refreshState, 2000);
  </script>
</body>
</html>
"""


WATCH_HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Watch __JAV_ID__</title>
  <style>
    body {
      margin: 0;
      font-family: "Avenir Next", "Segoe UI", sans-serif;
      background: linear-gradient(120deg, #0f172a, #1f2937);
      color: #f8fafc;
    }
    .wrap { max-width: 1100px; margin: 0 auto; padding: 20px; }
    a { color: #a7f3d0; text-decoration: none; }
    .player {
      margin-top: 12px;
      border-radius: 14px;
      overflow: hidden;
      border: 1px solid rgba(255,255,255,0.16);
      background: #000;
    }
    video { width: 100%; display: block; max-height: 76vh; }
  </style>
</head>
<body>
  <div class="wrap">
    <a href="/">← Back to library</a>
    <h2 style="margin:10px 0 0">__JAV_ID__</h2>
    <div class="player">
      <video controls autoplay playsinline src="/api/local-video?id=__JAV_ID__"></video>
    </div>
  </div>
</body>
</html>
"""

