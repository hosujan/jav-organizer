from __future__ import annotations


def _layout(title: str, active: str, content: str, script: str = "") -> str:
    nav_links = [
        ("organize", "/organize", "Organize"),
        ("view", "/view", "Browse"),
    ]
    nav = "".join(
        f'<a class="nav-link {"active" if key == active else ""}" href="{href}">{label}</a>'
        for key, href, label in nav_links
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title}</title>
  <style>
    :root {{
      --bg: #070f18;
      --bg-2: #111a25;
      --surface: #162231;
      --surface-2: #1c2c3d;
      --line: #2f445c;
      --line-soft: #3b5470;
      --ink: #edf6ff;
      --muted: #9db1c7;
      --brand: #0e9f9a;
      --brand-2: #11786d;
      --accent: #f97316;
      --warn: #d97706;
      --good: #10b981;
    }}
    * {{ box-sizing: border-box; }}
    html, body {{ margin: 0; padding: 0; }}
    body {{
      color: var(--ink);
      font-family: "Space Grotesk", "Avenir Next", "Trebuchet MS", sans-serif;
      background:
        radial-gradient(circle at 12% -4%, rgba(14, 159, 154, 0.24) 0, transparent 34%),
        radial-gradient(circle at 92% 8%, rgba(249, 115, 22, 0.21) 0, transparent 28%),
        linear-gradient(180deg, var(--bg), var(--bg-2));
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      letter-spacing: 0.01em;
    }}
    a {{ color: inherit; }}
    .navbar {{
      position: sticky;
      top: 0;
      z-index: 40;
      backdrop-filter: blur(12px);
      background: rgba(7, 15, 24, 0.77);
      border-bottom: 1px solid rgba(59, 84, 112, 0.75);
    }}
    .nav-inner {{
      max-width: 1360px;
      margin: 0 auto;
      padding: 12px 18px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
    }}
    .brand {{
      text-decoration: none;
      display: flex;
      align-items: baseline;
      gap: 7px;
      font-weight: 800;
      color: #f4fbff;
    }}
    .brand-main {{
      text-transform: uppercase;
      letter-spacing: 0.12em;
      font-size: 13px;
    }}
    .brand-sub {{
      color: #8fc5d1;
      font-size: 11px;
      letter-spacing: 0.09em;
      text-transform: uppercase;
      opacity: 0.85;
    }}
    .nav-links {{ display: flex; gap: 8px; align-items: center; }}
    .nav-link {{
      text-decoration: none;
      font-size: 13px;
      border-radius: 999px;
      border: 1px solid transparent;
      padding: 7px 11px;
      color: var(--muted);
      transition: all .2s ease;
    }}
    .nav-link:hover {{
      border-color: var(--line);
      background: rgba(255,255,255,0.04);
      color: var(--ink);
    }}
    .nav-link.active {{
      color: #fff;
      border-color: rgba(14, 159, 154, 0.7);
      background: linear-gradient(130deg, rgba(14, 159, 154, 0.9), rgba(17, 120, 109, 0.95));
      box-shadow: 0 8px 22px rgba(14, 159, 154, 0.26);
    }}
    .shell {{
      max-width: 1360px;
      width: 100%;
      margin: 0 auto;
      padding: 18px 18px 26px;
      animation: page-enter .4s ease;
    }}
    @keyframes page-enter {{
      from {{ transform: translateY(8px); opacity: 0; }}
      to {{ transform: translateY(0); opacity: 1; }}
    }}
    .panel {{
      background: linear-gradient(180deg, rgba(22, 34, 49, 0.96), rgba(26, 40, 57, 0.96));
      border: 1px solid var(--line);
      border-radius: 16px;
      box-shadow: 0 16px 36px rgba(3, 8, 15, 0.45);
      padding: 16px;
    }}
    .page-head {{
      display: flex;
      gap: 12px;
      align-items: flex-end;
      justify-content: space-between;
      flex-wrap: wrap;
    }}
    .page-kicker {{
      margin: 0;
      color: #8fc5d1;
      text-transform: uppercase;
      letter-spacing: .15em;
      font-size: 10px;
      font-weight: 700;
    }}
    .page-title {{
      margin: 8px 0 0;
      font-size: 32px;
      line-height: 1.08;
      letter-spacing: 0.01em;
    }}
    .hint {{ color: var(--muted); font-size: 13px; }}
    button, input {{
      font: inherit;
      color: var(--ink);
      border-radius: 10px;
      border: 1px solid var(--line);
      background: #101a27;
      padding: 10px 12px;
    }}
    button {{ cursor: pointer; transition: all .2s ease; }}
    button:hover {{ border-color: var(--line-soft); }}
    button.primary {{
      color: #fff;
      border-color: rgba(14, 159, 154, 0.8);
      background: linear-gradient(130deg, var(--brand), var(--brand-2));
      font-weight: 700;
    }}
    button.primary:hover {{
      filter: brightness(1.03);
      box-shadow: 0 10px 22px rgba(14, 159, 154, 0.3);
    }}
    .pill {{
      display: inline-flex;
      align-items: center;
      border-radius: 999px;
      border: 1px solid #3c5a7b;
      background: rgba(13, 28, 43, 0.9);
      color: #c6defc;
      font-size: 11px;
      padding: 3px 9px;
    }}
    .card {{
      text-decoration: none;
      color: inherit;
      border-radius: 14px;
      overflow: hidden;
      background: #101b2a;
      border: 1px solid var(--line);
      display: flex;
      flex-direction: column;
      min-width: 0;
      transition: transform .2s ease, box-shadow .2s ease, border-color .2s ease;
    }}
    .card:hover {{
      transform: translateY(-4px);
      border-color: #426287;
      box-shadow: 0 18px 28px rgba(4, 10, 20, 0.5);
    }}
    .card-thumb {{
      aspect-ratio: 16 / 9;
      background: #152233;
      position: relative;
      overflow: hidden;
    }}
    .card-thumb > img,
    .card-thumb > video {{
      position: absolute;
      inset: 0;
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
    }}
    .card-thumb > video {{
      opacity: 0;
      transition: opacity .24s ease;
    }}
    .card-meta {{
      padding: 10px 12px 12px;
      display: grid;
      gap: 6px;
    }}
    .card-title {{
      font-weight: 700;
      font-size: 14px;
      line-height: 1.34;
      min-height: calc(1.34em * 2);
      display: -webkit-box;
      -webkit-line-clamp: 2;
      line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }}
    .card-sub {{
      color: var(--muted);
      font-size: 12px;
      min-height: calc(1.3em * 2);
    }}
    .fact-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 9px 12px;
    }}
    .fact {{
      border: 1px solid #314a66;
      background: #101b2b;
      border-radius: 12px;
      padding: 9px 10px;
    }}
    .fact-label {{
      margin: 0 0 4px;
      text-transform: uppercase;
      letter-spacing: .09em;
      color: #8eb1db;
      font-size: 10px;
      font-weight: 700;
    }}
    .fact-value {{ color: #e8f2ff; font-size: 13px; word-break: break-word; }}
    .chip-list {{ display: flex; flex-wrap: wrap; gap: 6px; }}
    .chip {{
      border-radius: 999px;
      border: 1px solid #3b5678;
      background: #132337;
      color: #d3e7ff;
      padding: 4px 9px;
      font-size: 12px;
    }}
    .plot {{ margin: 0; color: #d5e4f8; font-size: 13px; line-height: 1.6; white-space: pre-wrap; }}
    .footer {{
      margin-top: auto;
      border-top: 1px solid rgba(59, 84, 112, 0.72);
      background: rgba(8, 14, 22, 0.5);
      color: #94abc1;
      font-size: 12px;
    }}
    .footer-inner {{ max-width: 1360px; margin: 0 auto; padding: 10px 18px 14px; }}

    @media (max-width: 1040px) {{
      .page-title {{ font-size: 27px; }}
      #heroStage {{ grid-template-columns: 1fr !important; }}
      #heroPosterPanel {{ min-height: 240px !important; max-height: 340px; }}
      .detail-grid {{ grid-template-columns: 1fr !important; }}
      .fact-grid {{ grid-template-columns: 1fr; }}
      #watchGrid {{ grid-template-columns: 1fr !important; }}
      #screenshotsGrid {{ grid-template-columns: repeat(2, minmax(0, 1fr)) !important; }}
    }}

    @media (max-width: 760px) {{
      .nav-inner {{ padding: 10px 12px; }}
      .shell {{ padding: 14px 12px 20px; }}
      .brand-sub {{ display: none; }}
      .page-title {{ font-size: 23px; }}
      #searchInput {{ min-width: 0 !important; width: 100%; }}
      #grid {{ grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)) !important; gap: 10px !important; }}
      #rails [data-rail-track] {{ grid-auto-columns: minmax(210px, 84vw) !important; }}
      #heroTitle {{ font-size: 24px !important; }}
      #watchTitle {{ font-size: 24px !important; }}
      #screenshotsGrid {{ grid-template-columns: 1fr !important; }}
      .watch-actions a {{ width: 100%; text-align: center; }}
      .detail-actions a, .detail-actions button {{ width: 100%; text-align: center; }}
    }}
  </style>
</head>
<body>
  <header class="navbar">
    <div class="nav-inner">
      <a class="brand" href="/organize">
        <span class="brand-main">JAV Organizer</span>
        <span class="brand-sub">Local Cinema</span>
      </a>
      <nav class="nav-links">{nav}</nav>
    </div>
  </header>
  <main class="shell">{content}</main>
  <footer class="footer">
    <div class="footer-inner">Local-only media workflow. Stream from your own library without uploading anything.</div>
  </footer>
  {script}
</body>
</html>
"""


ORGANIZE_HTML = _layout(
    "JAV Organizer",
    "organize",
    """
  <section class="panel">
    <h1 style="margin:0 0 8px; font-size:26px; letter-spacing:.05em; text-transform:uppercase;">Organize</h1>
    <p class="hint" style="margin:0 0 14px;">Scan your folder, process metadata/media, then verify history entries.</p>
    <div style="display:flex; gap:8px; flex-wrap:wrap; align-items:center;">
      <button id="chooseBtn" class="primary">Choose Local Directory</button>
      <input id="manualPath" type="text" placeholder="Fallback: enter local path" style="min-width:320px; flex:1;" />
      <button id="manualBtn">Use Path</button>
      <button id="processBtn" class="primary">Start Processing</button>
    </div>
    <p id="status" class="hint" style="margin:10px 0 0;"></p>
  </section>

  <section class="panel" style="margin-top:14px;">
    <div style="display:flex; justify-content:space-between; gap:10px; align-items:center; margin-bottom:8px;">
      <strong>Progress</strong>
      <span id="progressText" class="hint"></span>
    </div>
    <div id="logs" style="background:#08121d; color:#bbf7d0; font-family:ui-monospace, SFMono-Regular, Menlo, monospace; border-radius:10px; border:1px solid #263f56; padding:10px; min-height:180px; max-height:220px; overflow:auto; white-space:pre-wrap; font-size:12px;"></div>
  </section>

  <section class="panel" style="margin-top:14px;">
    <div style="display:flex; justify-content:space-between; gap:10px; align-items:center;">
      <strong>Catalog History</strong>
      <span class="hint" id="catalogCount"></span>
    </div>
    <div style="overflow:auto; margin-top:10px;">
      <table style="width:100%; border-collapse:collapse; min-width:700px; font-size:13px;">
        <thead>
          <tr style="text-align:left; border-bottom:1px solid var(--line);">
            <th style="padding:8px 6px;">JAV ID</th>
            <th style="padding:8px 6px;">Title</th>
            <th style="padding:8px 6px;">Release</th>
            <th style="padding:8px 6px;">Publisher</th>
            <th style="padding:8px 6px;">Assets</th>
            <th style="padding:8px 6px;">Play</th>
          </tr>
        </thead>
        <tbody id="historyBody"></tbody>
      </table>
    </div>
  </section>
""",
    """
  <script>
    const statusEl = document.getElementById("status");
    const progressEl = document.getElementById("progressText");
    const logsEl = document.getElementById("logs");
    const chooseBtn = document.getElementById("chooseBtn");
    const processBtn = document.getElementById("processBtn");
    const manualBtn = document.getElementById("manualBtn");
    const manualPath = document.getElementById("manualPath");
    const historyBody = document.getElementById("historyBody");
    const catalogCount = document.getElementById("catalogCount");

    async function post(url, body) {
      const res = await fetch(url, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(body || {}),
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

    function renderLogs(lines) {
      logsEl.textContent = lines.join("\\n");
      logsEl.scrollTop = logsEl.scrollHeight;
    }

    function renderHistory(videos) {
      historyBody.innerHTML = "";
      catalogCount.textContent = videos.length + " record(s)";
      for (const v of videos) {
        const tr = document.createElement("tr");
        tr.style.borderBottom = "1px solid var(--line)";
        const assets = [
          v.has_poster_local ? "poster" : null,
          v.has_preview_local ? "preview" : null,
          v.has_local_video ? "video" : null,
        ].filter(Boolean).join(", ") || "none";
        tr.innerHTML = `
          <td style="padding:8px 6px; font-weight:700;">${v.jav_id}</td>
          <td style="padding:8px 6px;">${v.title || "Untitled"}</td>
          <td style="padding:8px 6px;">${v.release_date || "-"}</td>
          <td style="padding:8px 6px;">${v.publisher || "-"}</td>
          <td style="padding:8px 6px; color:var(--muted);">${assets}</td>
          <td style="padding:8px 6px;"><a href="/video/${encodeURIComponent(v.jav_id)}">Open</a></td>
        `;
        historyBody.appendChild(tr);
      }
    }

    async function chooseDir() {
      try {
        const data = await post("/api/select-directory", {});
        statusEl.textContent = "Selected: " + data.selected_dir + " (" + data.count + " matched videos)";
        await refresh();
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
        await refresh();
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

    async function refresh() {
      const [state, videos] = await Promise.all([get("/api/state"), get("/api/videos")]);
      const current = state.current ? " current: " + state.current : "";
      progressEl.textContent = state.processed + " / " + state.total + (state.processing ? " (running)" : " (idle)") + current;
      renderLogs(state.logs || []);
      renderHistory(videos || []);
    }

    chooseBtn.addEventListener("click", chooseDir);
    manualBtn.addEventListener("click", chooseManual);
    processBtn.addEventListener("click", startProcess);

    refresh();
    setInterval(refresh, 2000);
  </script>
""",
)


VIEW_HTML = _layout(
    "JAV Viewing",
    "view",
    """
  <section class="panel" style="padding:0; overflow:hidden; background:linear-gradient(125deg, rgba(9, 52, 65, 0.95), rgba(24, 36, 56, 0.96)); border-color:#3d6281;">
    <div id="heroStage" style="display:grid; grid-template-columns:minmax(260px, 32%) minmax(0, 1fr);">
      <div id="heroPosterPanel" style="position:relative; min-height:260px; background:#0d1622;">
        <img id="heroPoster" src="" alt="" style="position:absolute; inset:0; width:100%; height:100%; object-fit:cover; display:block;" />
        <div style="position:absolute; inset:auto 12px 12px 12px; display:flex; justify-content:space-between; gap:8px; align-items:center;">
          <span id="heroJavBadge" class="pill" style="background:rgba(8, 19, 32, 0.78); border-color:#42688a;"></span>
          <span class="pill" style="background:rgba(16, 185, 129, 0.14); border-color:rgba(16, 185, 129, 0.5); color:#aef5d4;">Featured</span>
        </div>
      </div>
      <div style="padding:20px 20px 22px;">
        <div class="page-head" style="align-items:flex-start;">
          <div>
            <p class="page-kicker">Browse</p>
            <h1 id="heroTitle" class="page-title" style="font-size:34px;">Your Local Streaming Shelf</h1>
          </div>
          <input id="searchInput" type="search" placeholder="Search by JAV ID or title" style="min-width:300px; max-width:450px; width:100%; background:#12263b; border-color:#426486;" />
        </div>
        <p id="heroMeta" style="margin:12px 0 0; color:#bfdaf4; font-size:14px; line-height:1.5;"></p>
        <div style="margin-top:18px; display:flex; gap:10px; flex-wrap:wrap;">
          <a id="heroPlay" href="#" style="text-decoration:none; color:#fff; border:1px solid rgba(16, 185, 129, 0.55); background:linear-gradient(125deg, #10b981, #0f766e); border-radius:10px; padding:10px 14px; font-weight:700;">Play Now</a>
          <a id="heroInfo" href="#" style="text-decoration:none; color:#ffdcb8; border:1px solid rgba(249, 115, 22, 0.52); background:rgba(249, 115, 22, 0.1); border-radius:10px; padding:10px 14px; font-weight:700;">Open Details</a>
        </div>
      </div>
    </div>
  </section>

  <section id="rails" style="margin-top:14px;"></section>

  <section class="panel" style="margin-top:14px;">
    <div style="display:flex; justify-content:space-between; align-items:center; gap:10px; margin-bottom:10px;">
      <strong>All Titles</strong>
      <span class="hint" id="resultCount"></span>
    </div>
    <div id="grid" style="display:grid; grid-template-columns:repeat(auto-fill, minmax(240px, 1fr)); gap:14px;"></div>
  </section>
""",
    """
  <script>
    const gridEl = document.getElementById("grid");
    const railsEl = document.getElementById("rails");
    const searchInput = document.getElementById("searchInput");
    const resultCountEl = document.getElementById("resultCount");
    const heroPosterEl = document.getElementById("heroPoster");
    const heroJavBadgeEl = document.getElementById("heroJavBadge");
    const heroTitleEl = document.getElementById("heroTitle");
    const heroMetaEl = document.getElementById("heroMeta");
    const heroPlayEl = document.getElementById("heroPlay");
    const heroInfoEl = document.getElementById("heroInfo");

    let allVideos = [];
    let activeRailScroller = null;

    async function get(url) {
      const res = await fetch(url);
      if (!res.ok) throw new Error(res.statusText);
      return res.json();
    }

    function escapeHtml(text) {
      return (text || "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;");
    }

    function toDetail(v) {
      return "/video/" + encodeURIComponent(v.jav_id);
    }

    function toWatch(v) {
      return "/watch/" + encodeURIComponent(v.jav_id);
    }

    function safeNumber(value, fallback = 0) {
      const n = Number(value);
      return Number.isFinite(n) ? n : fallback;
    }

    function formatDuration(sec) {
      const total = Math.max(0, Math.floor(safeNumber(sec, 0)));
      const h = Math.floor(total / 3600);
      const m = Math.floor((total % 3600) / 60);
      const s = total % 60;
      if (h > 0) {
        return `${h}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
      }
      return `${m}:${String(s).padStart(2, "0")}`;
    }

    function valueTime(value) {
      const t = Date.parse(value || "");
      return Number.isFinite(t) ? t : 0;
    }

    function byRecent(a, b) {
      return (b.release_date || "").localeCompare(a.release_date || "");
    }

    function pickFeatured(videos) {
      if (!videos.length) return null;
      return [...videos].sort((a, b) => {
        const scoreDiff = safeNumber(b.recommendation_score) - safeNumber(a.recommendation_score);
        if (scoreDiff) return scoreDiff;
        return byRecent(a, b);
      })[0];
    }

    function cardMarkup(v) {
      const progress = Math.max(0, Math.min(100, safeNumber(v.progress_percent, 0)));
      const isResume = progress >= 3 && progress < 96;
      const isCompleted = progress >= 96;
      const statusLabel = isCompleted
        ? "Completed"
        : (isResume ? ("Resume " + Math.round(progress) + "%") : "New");
      const statusStyle = isCompleted
        ? "background:rgba(148, 163, 184, 0.18); border-color:rgba(148, 163, 184, 0.5); color:#e2e8f0;"
        : (isResume
          ? "background:rgba(249, 115, 22, 0.16); border-color:rgba(249, 115, 22, 0.56); color:#ffd7b0;"
          : "background:rgba(16, 185, 129, 0.14); border-color:rgba(16, 185, 129, 0.55); color:#aef5d4;");
      const timeHint = isResume ? formatDuration(v.progress_sec || 0) : "";
      return `
        <div class="card-thumb">
          <img src="${v.poster_url}" alt="${escapeHtml(v.jav_id)}" loading="lazy" />
          <video muted loop playsinline preload="none" src="${v.preview_url}"></video>
          <div style="position:absolute; inset:auto 0 0; padding:7px 8px; background:linear-gradient(180deg, transparent, rgba(0,0,0,.8)); display:flex; justify-content:space-between; gap:8px;">
            <span class="pill" style="background:rgba(5, 14, 22, 0.8); border-color:#45698b;">${escapeHtml(v.jav_id)}</span>
            <span class="pill" style="${statusStyle}">${statusLabel}</span>
          </div>
        </div>
        <div class="card-meta">
          <div class="card-title">${escapeHtml(v.title || "Untitled")}</div>
          <div class="card-sub">${escapeHtml(v.release_date || "-")} ${escapeHtml(v.publisher || "")}</div>
          ${isResume ? `<div class="hint" style="font-size:12px; margin-top:1px;">Continue from ${timeHint}</div>` : ""}
          <div style="margin-top:4px; height:4px; width:100%; border-radius:999px; background:rgba(191, 219, 254, 0.18); overflow:hidden;">
            <div style="height:100%; width:${progress}%; background:linear-gradient(90deg, #22d3ee, #0ea5a4);"></div>
          </div>
        </div>
      `;
    }

    function attachCardEffects(card) {
      const preview = card.querySelector("video");
      card.addEventListener("mouseenter", () => {
        preview.style.opacity = "1";
        preview.play().catch(() => {});
      });
      card.addEventListener("mouseleave", () => {
        preview.style.opacity = "0";
        preview.pause();
        preview.currentTime = 0;
      });
    }

    function makeCard(v) {
      const card = document.createElement("a");
      card.className = "card";
      card.href = toDetail(v);
      card.innerHTML = cardMarkup(v);
      attachCardEffects(card);
      return card;
    }

    function renderHero(video) {
      if (!video) {
        heroPosterEl.src = "";
        heroJavBadgeEl.textContent = "No Match";
        heroTitleEl.textContent = "No videos found";
        heroMetaEl.textContent = "Try a different search term.";
        heroPlayEl.style.display = "none";
        heroInfoEl.style.display = "none";
        return;
      }

      heroPosterEl.src = video.poster_url;
      heroPosterEl.alt = video.jav_id;
      heroJavBadgeEl.textContent = video.jav_id;
      heroTitleEl.textContent = video.title ? video.title : video.jav_id;
      const progress = safeNumber(video.progress_percent, 0);
      const watchHint = progress >= 3 && progress < 96
        ? ("Resume at " + formatDuration(video.progress_sec || 0))
        : (progress >= 96 ? "Watched" : "Start watching");
      const metaBits = [video.jav_id, video.release_date || "Unknown date", video.publisher || "Unknown publisher", watchHint];
      heroMetaEl.textContent = metaBits.join(" / ");
      heroInfoEl.href = toDetail(video);
      heroPlayEl.href = toWatch(video);
      heroPlayEl.style.display = "inline-flex";
      heroInfoEl.style.display = "inline-flex";
    }

    function renderGrid(videos) {
      gridEl.innerHTML = "";
      resultCountEl.textContent = videos.length + " title(s)";
      for (const video of videos) {
        gridEl.appendChild(makeCard(video));
      }
    }

    function scrollRail(scroller, direction) {
      if (!scroller) return;
      const amount = Math.max(260, Math.floor(scroller.clientWidth * 0.82));
      scroller.scrollBy({left: amount * direction, behavior: "smooth"});
    }

    function buildRail(name, items) {
      const section = document.createElement("section");
      section.className = "panel";
      section.style.marginBottom = "14px";
      section.innerHTML = `
        <div style="display:flex; align-items:center; justify-content:space-between; gap:10px; margin-bottom:10px;">
          <strong>${escapeHtml(name)}</strong>
          <div style="display:flex; gap:6px;">
            <button type="button" data-dir="-1" style="padding:6px 10px; min-width:42px;">&#8592;</button>
            <button type="button" data-dir="1" style="padding:6px 10px; min-width:42px;">&#8594;</button>
          </div>
        </div>
        <div data-rail-track style="display:grid; grid-auto-flow:column; grid-auto-columns:minmax(230px, 1fr); gap:12px; overflow-x:auto; padding-bottom:6px; outline:none;"></div>
      `;
      const scroller = section.querySelector("[data-rail-track]");
      for (const video of items) {
        scroller.appendChild(makeCard(video));
      }
      scroller.addEventListener("mouseenter", () => { activeRailScroller = scroller; });
      scroller.addEventListener("focus", () => { activeRailScroller = scroller; });
      const buttons = section.querySelectorAll("button[data-dir]");
      for (const button of buttons) {
        button.addEventListener("click", () => {
          activeRailScroller = scroller;
          scrollRail(scroller, Number(button.dataset.dir || "0"));
        });
      }
      if (!activeRailScroller) activeRailScroller = scroller;
      return section;
    }

    function buildRails(videos) {
      railsEl.innerHTML = "";
      activeRailScroller = null;
      if (!videos.length) return;

      const fresh = [...videos].filter((v) => !!v.release_date).sort(byRecent).slice(0, 14);
      const continueWatching = [...videos]
        .filter((v) => {
          const p = safeNumber(v.progress_percent, 0);
          return p >= 3 && p < 96;
        })
        .sort((a, b) => valueTime(b.progress_updated_at) - valueTime(a.progress_updated_at))
        .slice(0, 14);
      const topPicks = [...videos]
        .sort((a, b) => safeNumber(b.recommendation_score, 0) - safeNumber(a.recommendation_score, 0))
        .slice(0, 14);
      const withPreview = [...videos].filter((v) => v.has_preview_local).sort(byRecent).slice(0, 14);
      const watchedCore = [...videos]
        .filter((v) => safeNumber(v.progress_percent, 0) >= 45)
        .sort((a, b) => valueTime(b.progress_updated_at) - valueTime(a.progress_updated_at))
        .slice(0, 8);

      const actressWeight = new Map();
      const genreWeight = new Map();
      const pubWeight = new Map();
      for (const item of watchedCore) {
        for (const name of (item.actresses || [])) {
          actressWeight.set(name, (actressWeight.get(name) || 0) + 1.4);
        }
        for (const name of (item.genres || [])) {
          genreWeight.set(name, (genreWeight.get(name) || 0) + 0.9);
        }
        if (item.publisher) {
          pubWeight.set(item.publisher, (pubWeight.get(item.publisher) || 0) + 0.8);
        }
      }
      const watchedIds = new Set(watchedCore.map((v) => v.jav_id));
      const becauseWatched = [...videos]
        .filter((v) => !watchedIds.has(v.jav_id))
        .map((v) => {
          let affinity = 0;
          for (const name of (v.actresses || [])) {
            affinity += actressWeight.get(name) || 0;
          }
          for (const name of (v.genres || [])) {
            affinity += genreWeight.get(name) || 0;
          }
          if (v.publisher) {
            affinity += pubWeight.get(v.publisher) || 0;
          }
          affinity += safeNumber(v.recommendation_score, 0) * 0.18;
          return {v, affinity};
        })
        .filter((entry) => entry.affinity > 0)
        .sort((a, b) => b.affinity - a.affinity)
        .slice(0, 14)
        .map((entry) => entry.v);

      if (continueWatching.length) railsEl.appendChild(buildRail("Continue Watching", continueWatching));
      if (topPicks.length) railsEl.appendChild(buildRail("Top Picks For You", topPicks));
      if (becauseWatched.length) railsEl.appendChild(buildRail("Because You Watched", becauseWatched));
      if (fresh.length) railsEl.appendChild(buildRail("New Releases", fresh));
      if (withPreview.length) railsEl.appendChild(buildRail("Preview Available", withPreview));
    }

    function applyFilter() {
      const query = searchInput.value.trim().toLowerCase();
      if (!query) {
        renderHero(pickFeatured(allVideos));
        buildRails(allVideos);
        renderGrid(allVideos);
        return;
      }

      const filtered = allVideos.filter((v) => {
        return (v.jav_id || "").toLowerCase().includes(query) || (v.title || "").toLowerCase().includes(query);
      });
      renderHero(pickFeatured(filtered));
      buildRails(filtered);
      renderGrid(filtered);
    }

    async function init() {
      allVideos = await get("/api/videos");
      renderHero(pickFeatured(allVideos));
      buildRails(allVideos);
      renderGrid(allVideos);
    }

    searchInput.addEventListener("input", applyFilter);
    document.addEventListener("keydown", (event) => {
      if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") return;
      const tag = event.target && event.target.tagName ? event.target.tagName.toLowerCase() : "";
      if (tag === "input" || tag === "textarea") return;
      if (!activeRailScroller) return;
      event.preventDefault();
      scrollRail(activeRailScroller, event.key === "ArrowLeft" ? -1 : 1);
    });

    init().catch((error) => {
      gridEl.innerHTML = '<p class="hint">Failed to load catalog: ' + error.message + '</p>';
    });
  </script>
""",
)


VIDEO_HTML = _layout(
    "Video __JAV_ID__",
    "view",
    """
  <section class="panel" style="padding:0; overflow:hidden; background:linear-gradient(125deg, rgba(16, 35, 56, 0.98), rgba(11, 39, 48, 0.96)); border-color:#3c617f;">
    <div style="display:grid; grid-template-columns:minmax(230px, 30%) minmax(0, 1fr);" class="detail-grid">
      <div style="position:relative; min-height:230px; background:#0b1622;">
        <img id="detailPoster" src="/api/poster?id=__JAV_ID__" alt="__JAV_ID__ poster" style="position:absolute; inset:0; width:100%; height:100%; object-fit:cover; display:block;" />
        <div style="position:absolute; inset:auto 12px 12px 12px; display:flex; justify-content:space-between; gap:8px;">
          <span id="detailIdPill" class="pill" style="background:rgba(8, 19, 32, 0.8); border-color:#3f6384;">__JAV_ID__</span>
          <span class="pill" style="background:rgba(14, 159, 154, 0.14); border-color:rgba(14, 159, 154, 0.58); color:#b6f5ef;">Details</span>
        </div>
      </div>
      <div style="padding:18px 20px 20px;">
        <div class="page-head" style="align-items:flex-start;">
          <div>
            <p class="page-kicker">Video Details</p>
            <h1 id="detailTitle" class="page-title" style="margin-top:6px;">__JAV_ID__</h1>
          </div>
          <div class="detail-actions" style="display:flex; gap:8px; flex-wrap:wrap;">
            <button id="detailPlayBtn" type="button" class="primary" style="padding:10px 14px;">Play Full Video</button>
            <a id="theaterLink" href="/watch/__JAV_ID__" style="text-decoration:none; color:#ffdcb8; border:1px solid rgba(249, 115, 22, 0.52); background:rgba(249, 115, 22, 0.1); border-radius:10px; padding:10px 14px; font-weight:700;">Open Theater</a>
            <a href="/view" style="text-decoration:none; color:#d5e7ff; border:1px solid #426486; background:#16293d; border-radius:10px; padding:10px 14px;">Back to Browse</a>
          </div>
        </div>
        <p id="detailMeta" style="margin:10px 0 0; color:#bfd7f2; font-size:14px;"></p>
        <p id="detailStatus" class="hint" style="margin:6px 0 0; color:#b6f5ef;">Preview loaded. Full playback available on demand.</p>
      </div>
    </div>
  </section>

  <section class="detail-grid" style="display:grid; grid-template-columns:minmax(0, 1.8fr) minmax(300px, 1fr); gap:14px; margin-top:14px;">
    <article class="panel" style="padding:0; overflow:hidden;">
      <div id="heroMediaWrap" style="width:100%; aspect-ratio:16 / 9; background:#05080f;">
        <video id="detailPreview" muted loop autoplay playsinline controls preload="metadata" src="/api/preview?id=__JAV_ID__" style="width:100%; height:100%; object-fit:contain; background:#000; display:block;"></video>
      </div>
      <div style="padding:12px 14px; border-top:1px solid #2f455e; color:#9db6d1; font-size:12px;">
        Inline preview clip. Use <strong style="color:#e6f3ff;">Play Full Video</strong> for the main local file.
      </div>
    </article>

    <article class="panel">
      <h2 style="margin:0 0 10px; font-size:18px;">Metadata</h2>
      <div id="detailFacts" class="fact-grid"></div>
    </article>
  </section>

  <section class="panel" style="margin-top:14px;">
    <h2 style="margin:0 0 10px; font-size:18px;">Cast & Tags</h2>
    <div style="display:grid; gap:12px;">
      <div>
        <div class="fact-label">Actresses</div>
        <div id="detailActresses" class="chip-list"></div>
      </div>
      <div>
        <div class="fact-label">Genres</div>
        <div id="detailGenres" class="chip-list"></div>
      </div>
      <div>
        <div class="fact-label">Plot</div>
        <p id="detailPlot" class="plot">-</p>
      </div>
    </div>
  </section>

  <section class="panel" style="margin-top:14px;">
    <div style="display:flex; justify-content:space-between; align-items:center; gap:10px; margin-bottom:10px;">
      <h2 style="margin:0; font-size:18px;">Screenshots</h2>
      <span class="hint" id="screenshotCount">0 image(s)</span>
    </div>
    <div id="screenshotsGrid" style="display:grid; grid-template-columns:repeat(3, minmax(0, 1fr)); gap:10px;"></div>
  </section>
""",
    """
  <script>
    function escapeHtml(text) {
      return (text || "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;");
    }

    async function get(url) {
      const res = await fetch(url);
      if (!res.ok) throw new Error(res.statusText);
      return res.json();
    }

    function renderChips(containerId, items) {
      const el = document.getElementById(containerId);
      if (!el) return;
      el.innerHTML = "";
      const values = Array.isArray(items) ? items.filter(Boolean) : [];
      if (!values.length) {
        const none = document.createElement("span");
        none.className = "hint";
        none.textContent = "-";
        el.appendChild(none);
        return;
      }
      for (const item of values) {
        const chip = document.createElement("span");
        chip.className = "chip";
        chip.textContent = item;
        el.appendChild(chip);
      }
    }

    function renderFacts(data) {
      const factsEl = document.getElementById("detailFacts");
      if (!factsEl) return;

      const facts = [
        ["JAV ID", data.jav_id, false],
        ["Release Date", data.release_date, false],
        ["Duration", data.duration_min ? (data.duration_min + " min") : null, false],
        ["Publisher", data.publisher, false],
        ["Label", data.label, false],
        ["Series", data.series, false],
        ["Director", data.director, false],
        ["Rating", data.rating != null ? String(data.rating) : null, false],
        ["Local Video", data.has_local_video ? "Yes" : "No", false],
        ["Watch Progress", Math.round(Number(data.progress_percent || 0)) + "%", false],
        ["Watch State", data.watch_state || "started", false],
        ["Fetched At", data.fetched_at, false],
        ["Source", data.page_url ? `<a href="${escapeHtml(data.page_url)}" target="_blank" rel="noopener noreferrer">Open source page</a>` : "-", true],
      ];

      factsEl.innerHTML = "";
      for (const [label, value, isHtml] of facts) {
        const rendered = value ? (isHtml ? value : escapeHtml(value)) : "-";
        const fact = document.createElement("div");
        fact.className = "fact";
        fact.innerHTML = `
          <p class="fact-label">${escapeHtml(label)}</p>
          <div class="fact-value">${rendered}</div>
        `;
        factsEl.appendChild(fact);
      }
    }

    function renderScreenshots(items) {
      const screenshots = Array.isArray(items) ? items.filter(Boolean) : [];
      const grid = document.getElementById("screenshotsGrid");
      const countEl = document.getElementById("screenshotCount");
      if (!grid || !countEl) return;
      grid.innerHTML = "";
      countEl.textContent = screenshots.length + " image(s)";

      if (!screenshots.length) {
        const msg = document.createElement("p");
        msg.className = "hint";
        msg.textContent = "No screenshots available.";
        grid.appendChild(msg);
        return;
      }

      for (const src of screenshots) {
        const item = document.createElement("a");
        item.href = src;
        item.target = "_blank";
        item.rel = "noopener noreferrer";
        item.style.display = "block";
        item.style.overflow = "hidden";
        item.style.borderRadius = "12px";
        item.style.border = "1px solid #2f465e";
        item.style.background = "#0b1622";

        const img = document.createElement("img");
        img.src = src;
        img.alt = "Screenshot";
        img.loading = "lazy";
        img.style.display = "block";
        img.style.width = "100%";
        img.style.aspectRatio = "16 / 9";
        img.style.objectFit = "cover";
        img.style.transition = "transform .2s ease";

        item.addEventListener("mouseenter", () => {
          img.style.transform = "scale(1.03)";
        });
        item.addEventListener("mouseleave", () => {
          img.style.transform = "scale(1)";
        });

        item.appendChild(img);
        grid.appendChild(item);
      }
    }

    function loadMainVideo() {
      const wrap = document.getElementById("heroMediaWrap");
      const statusEl = document.getElementById("detailStatus");
      if (!wrap || wrap.dataset.loaded === "1") return;

      const video = document.createElement("video");
      video.controls = true;
      video.autoplay = true;
      video.playsInline = true;
      video.src = "/api/local-video?id=__JAV_ID__";
      video.style.width = "100%";
      video.style.height = "100%";
      video.style.objectFit = "contain";
      video.style.background = "#000";
      video.style.display = "block";

      wrap.innerHTML = "";
      wrap.appendChild(video);
      wrap.dataset.loaded = "1";

      if (statusEl) {
        statusEl.textContent = "Full local video loaded.";
      }
    }

    async function initDetail() {
      try {
        const data = await get("/api/video?id=__JAV_ID__");
        if (!data || !data.jav_id) return;

        const title = data.title ? data.jav_id + " - " + data.title : data.jav_id;
        document.getElementById("detailTitle").textContent = title;
        document.getElementById("detailIdPill").textContent = data.jav_id;
        document.getElementById("detailPlot").textContent = data.plot || "-";
        renderFacts(data);
        renderChips("detailActresses", data.actresses || []);
        renderChips("detailGenres", data.genres || []);
        renderScreenshots(data.screenshots || []);

        const metaBits = [data.release_date || null, data.publisher || null].filter(Boolean);
        document.getElementById("detailMeta").textContent = metaBits.join(" / ");
        const statusEl = document.getElementById("detailStatus");
        const progress = Number(data.progress_percent || 0);
        if (statusEl && progress >= 3 && progress < 96) {
          statusEl.textContent = "Resume available at " + Math.floor(Number(data.progress_sec || 0)) + " sec (" + Math.round(progress) + "%).";
        }
        document.getElementById("detailPoster").src = data.poster_url || "/api/poster?id=__JAV_ID__";
        document.title = "Video " + title;
      } catch (error) {
        const meta = document.getElementById("detailMeta");
        if (meta) {
          meta.textContent = "Metadata unavailable.";
        }
      }
    }

    document.getElementById("detailPlayBtn").addEventListener("click", loadMainVideo);

    const preview = document.getElementById("detailPreview");
    if (preview) {
      preview.play().catch(() => {});
    }

    initDetail();
  </script>
""",
)


WATCH_HTML = _layout(
    "Watch __JAV_ID__",
    "view",
    """
  <section class="panel" style="padding:0; overflow:hidden; background:linear-gradient(122deg, rgba(13, 45, 62, 0.98), rgba(21, 34, 54, 0.96)); border-color:#3a5f7f;">
    <div id="watchGrid" style="display:grid; grid-template-columns:minmax(0, 2fr) minmax(280px, 1fr);">
      <div style="padding:18px; border-right:1px solid rgba(58, 95, 127, 0.55);">
        <p class="page-kicker" style="margin:0;">Now Playing</p>
        <h1 id="watchTitle" class="page-title" style="margin-top:7px;">__JAV_ID__</h1>
        <p id="watchMeta" style="margin:9px 0 0; color:#bdd8f2; font-size:14px;"></p>
        <div id="resumeBox" style="display:none; margin-top:10px; gap:8px; flex-wrap:wrap;">
          <button id="resumeBtn" type="button" class="primary" style="padding:8px 12px;">Resume</button>
          <button id="restartBtn" type="button" style="padding:8px 12px;">Start Over</button>
          <span id="resumeText" class="hint"></span>
        </div>

        <div style="margin-top:14px; border:1px solid #304e6b; border-radius:14px; overflow:hidden; background:#05070c; box-shadow:0 16px 34px rgba(0,0,0,.38);">
          <video id="watchPlayer" controls autoplay playsinline src="/api/local-video?id=__JAV_ID__" style="width:100%; max-height:74vh; display:block; background:#000;"></video>
        </div>
      </div>

      <aside style="padding:18px; display:grid; align-content:start; gap:12px; background:rgba(8, 18, 31, 0.55);">
        <div>
          <h2 style="margin:0; font-size:18px;">Quick Actions</h2>
          <p class="hint" style="margin:6px 0 0;">Stay in theater mode or jump back for metadata browsing.</p>
        </div>
        <div class="watch-actions" style="display:grid; gap:8px;">
          <a href="/video/__JAV_ID__" style="text-decoration:none; border:1px solid #3f6487; background:#17304a; color:#d8ecff; border-radius:10px; padding:10px 12px; font-weight:700;">Open Details</a>
          <a href="/view" style="text-decoration:none; border:1px solid #3f6487; background:#17304a; color:#d8ecff; border-radius:10px; padding:10px 12px;">Back to Browse</a>
        </div>

        <div class="panel" style="padding:12px; background:rgba(23, 48, 74, 0.45); border-color:#335676; box-shadow:none;">
          <p class="fact-label" style="margin-top:0;">Playback Tips</p>
          <p class="hint" style="margin:0; line-height:1.6;">Use left/right arrow keys for seeking and space for play/pause. Streaming uses HTTP range requests from your local media file.</p>
        </div>
      </aside>
    </div>
  </section>
""",
    """
  <script>
    async function get(url) {
      const res = await fetch(url);
      if (!res.ok) throw new Error(res.statusText);
      return res.json();
    }

    async function post(url, body, keepalive = false) {
      const res = await fetch(url, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(body || {}),
        keepalive,
      });
      if (!res.ok) throw new Error(res.statusText);
      return res.json().catch(() => ({}));
    }

    function safeNumber(value, fallback = 0) {
      const n = Number(value);
      return Number.isFinite(n) ? n : fallback;
    }

    function formatDuration(sec) {
      const total = Math.max(0, Math.floor(safeNumber(sec, 0)));
      const h = Math.floor(total / 3600);
      const m = Math.floor((total % 3600) / 60);
      const s = total % 60;
      if (h > 0) {
        return `${h}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
      }
      return `${m}:${String(s).padStart(2, "0")}`;
    }

    const player = document.getElementById("watchPlayer");
    const resumeBox = document.getElementById("resumeBox");
    const resumeBtn = document.getElementById("resumeBtn");
    const restartBtn = document.getElementById("restartBtn");
    const resumeText = document.getElementById("resumeText");

    let resumeAt = 0;
    let lastSavedSec = -1;

    async function saveProgress(eventName = "progress", keepalive = false) {
      if (!player) return;
      const position = safeNumber(player.currentTime, 0);
      const duration = safeNumber(player.duration, 0);
      const nowSec = Math.floor(position);
      if (!keepalive && eventName === "progress" && nowSec === lastSavedSec) return;
      if (!keepalive && eventName === "progress" && nowSec % 5 !== 0) return;
      lastSavedSec = nowSec;

      try {
        await post(
          "/api/watch-progress",
          {
            id: "__JAV_ID__",
            position_sec: position,
            duration_sec: duration > 0 ? duration : null,
            event: eventName,
          },
          keepalive,
        );
      } catch (error) {
      }
    }

    function showResume(positionSec, percent) {
      if (!resumeBox || !resumeBtn || !restartBtn || !resumeText || !player) return;
      if (!(positionSec >= 30 && percent < 96)) {
        resumeBox.style.display = "none";
        return;
      }
      resumeAt = positionSec;
      resumeText.textContent = `Resume from ${formatDuration(positionSec)} (${Math.round(percent)}%)`;
      resumeBox.style.display = "flex";
      resumeBtn.textContent = `Resume ${formatDuration(positionSec)}`;
      resumeBtn.onclick = () => {
        player.currentTime = Math.max(0, resumeAt - 2);
        resumeBox.style.display = "none";
        player.play().catch(() => {});
      };
      restartBtn.onclick = async () => {
        player.currentTime = 0;
        resumeBox.style.display = "none";
        await saveProgress("reset");
      };
    }

    async function initMeta() {
      try {
        const data = await get("/api/video?id=__JAV_ID__");
        if (!data || !data.jav_id) return;

        const title = data.title ? data.jav_id + " - " + data.title : data.jav_id;
        document.getElementById("watchTitle").textContent = title;

        const bits = [data.release_date || null, data.publisher || null, data.duration_min ? data.duration_min + " min" : null].filter(Boolean);
        document.getElementById("watchMeta").textContent = bits.join(" / ");
        showResume(safeNumber(data.progress_sec, 0), safeNumber(data.progress_percent, 0));
        document.title = "Watch " + title;
      } catch (error) {
        const meta = document.getElementById("watchMeta");
        if (meta) {
          meta.textContent = "Metadata unavailable.";
        }
      }
    }

    if (player) {
      player.addEventListener("timeupdate", () => {
        saveProgress("progress").catch(() => {});
      });
      player.addEventListener("pause", () => {
        saveProgress("progress").catch(() => {});
      });
      player.addEventListener("ended", () => {
        saveProgress("ended").catch(() => {});
      });
      player.play().catch(() => {});
    }
    window.addEventListener("beforeunload", () => {
      saveProgress("progress", true).catch(() => {});
    });

    initMeta();
  </script>
""",
)
