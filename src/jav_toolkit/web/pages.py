from __future__ import annotations


def _layout(title: str, active: str, content: str, script: str = "") -> str:
    nav_links = [
        ("organize", "/organize", "Organize"),
        ("view", "/view", "Browse"),
        ("titles", "/all-titles", "All Titles"),
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
      --control-bg: #0b1624;
      --control-bg-strong: #12243a;
      --warn: #d97706;
      --good: #10b981;
    }}
    * {{ box-sizing: border-box; }}
    html, body {{ margin: 0; padding: 0; overflow-x: hidden; }}
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
    .section-head {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      flex-wrap: wrap;
      margin-bottom: 10px;
    }}
    .stat-pill {{
      display: inline-flex;
      align-items: center;
      border-radius: 999px;
      border: 1px solid #4c6e91;
      background: rgba(10, 21, 35, 0.75);
      color: #d5e9ff;
      font-size: 12px;
      padding: 4px 10px;
    }}
    .empty-state {{
      border: 1px dashed #4d6e90;
      border-radius: 12px;
      padding: 18px 14px;
      color: #c2d6eb;
      text-align: center;
      background: rgba(9, 20, 32, 0.55);
      font-size: 13px;
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
    button, input, select {{
      font: inherit;
      color: var(--ink);
      border-radius: 10px;
      border: 1px solid #4a6480;
      background: var(--control-bg);
      padding: 10px 12px;
    }}
    button {{ cursor: pointer; transition: all .2s ease; }}
    button:hover {{ border-color: #6a89ab; }}
    button:focus-visible, input:focus-visible, select:focus-visible, a:focus-visible {{
      outline: 2px solid #e8f3ff;
      outline-offset: 2px;
    }}
    button.primary {{
      color: #fff;
      border-color: rgba(14, 159, 154, 0.95);
      background: linear-gradient(130deg, var(--brand), var(--brand-2));
      font-weight: 700;
      box-shadow: 0 10px 22px rgba(14, 159, 154, 0.22);
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
    .action-link {{
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      border: 1px solid #4e6e90;
      background: var(--control-bg-strong);
      color: #deeeff;
      border-radius: 10px;
      padding: 10px 14px;
      font-weight: 700;
      transition: border-color .2s ease, background .2s ease;
    }}
    .action-link:hover {{
      border-color: #79a0c7;
      background: #17344f;
    }}
    .panel-muted {{
      padding: 12px;
      background: rgba(11, 25, 41, 0.62);
      border-color: #3a5a79;
      box-shadow: none;
    }}
    .form-grid {{
      display: grid;
      grid-template-columns: minmax(240px, 1fr) auto auto auto auto;
      gap: 8px;
      align-items: center;
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
      #watchMain {{ border-right: none !important; border-bottom: 1px solid rgba(58, 95, 127, 0.55); }}
      #screenshotsGrid {{ grid-template-columns: repeat(2, minmax(0, 1fr)) !important; }}
      .form-grid {{ grid-template-columns: 1fr !important; }}
    }}

    @media (max-width: 760px) {{
      .nav-inner {{ padding: 10px 12px; }}
      .shell {{ padding: 14px 12px 20px; }}
      .brand-sub {{ display: none; }}
      .page-title {{ font-size: 23px; }}
      #searchInput {{ min-width: 0 !important; width: 100%; }}
      #grid {{ grid-template-columns: repeat(auto-fill, minmax(160px, 220px)) !important; justify-content: start !important; gap: 10px !important; }}
      #rails [data-rail-track] {{ grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)) !important; }}
      #heroTitle {{ font-size: 24px !important; }}
      #watchTitle {{ font-size: 24px !important; }}
      #screenshotsGrid {{ grid-template-columns: 1fr !important; }}
      .watch-actions a {{ width: 100%; text-align: center; }}
      .detail-actions a, .detail-actions button {{ width: 100%; text-align: center; }}
    }}
    @media (prefers-reduced-motion: reduce) {{
      *, *::before, *::after {{
        animation: none !important;
        transition: none !important;
      }}
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
    <p class="hint" style="margin:0 0 14px;">Choose your library path, then run one processing action.</p>
    <div class="form-grid">
      <input id="manualPath" type="text" placeholder="Fallback: enter local path" style="min-width:320px; flex:1;" />
      <button id="chooseBtn">Choose Local Directory</button>
      <button id="manualBtn">Use Path</button>
      <label style="display:flex; gap:8px; align-items:center; font-size:13px; color:var(--muted);">
        <input id="forceFetch" type="checkbox" style="width:16px; height:16px; padding:0;" />
        Force fetch all info + media
      </label>
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
    <div style="margin-top:10px;">
      <table style="width:100%; border-collapse:collapse; font-size:13px; table-layout:fixed;">
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
    const forceFetch = document.getElementById("forceFetch");
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
          <td style="padding:8px 6px; font-weight:700; overflow-wrap:anywhere;">${v.jav_id}</td>
          <td style="padding:8px 6px; overflow-wrap:anywhere;">${v.title || "Untitled"}</td>
          <td style="padding:8px 6px; overflow-wrap:anywhere;">${v.release_date || "-"}</td>
          <td style="padding:8px 6px; overflow-wrap:anywhere;">${v.publisher || "-"}</td>
          <td style="padding:8px 6px; color:var(--muted); overflow-wrap:anywhere;">${assets}</td>
          <td style="padding:8px 6px; overflow-wrap:anywhere;"><a href="/video/${encodeURIComponent(v.jav_id)}">Open</a></td>
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
        await post("/api/process", {force_override: Boolean(forceFetch.checked)});
        statusEl.textContent = "Processing started.";
      } catch (e) {
        statusEl.textContent = "Start failed: " + e.message;
      }
    }

    async function refresh() {
      const [state, videos] = await Promise.all([get("/api/state"), get("/api/videos")]);
      if (state.selected_dir) {
        manualPath.value = state.selected_dir;
        statusEl.textContent = "Selected: " + state.selected_dir + " (" + state.total + " matched videos)";
      }
      forceFetch.checked = Boolean(state.force_override);
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
          <a id="heroPlay" href="#" class="action-link" style="color:#fff; border-color:rgba(16, 185, 129, 0.7); background:linear-gradient(125deg, #10b981, #0f766e);">Play Now</a>
          <a id="heroInfo" href="#" class="action-link" style="color:#ffdcb8; border-color:rgba(249, 115, 22, 0.52); background:rgba(249, 115, 22, 0.1);">Open Details</a>
        </div>
      </div>
    </div>
  </section>

  <section class="panel" style="margin-top:14px;">
    <div class="section-head">
      <strong>Smart Discovery</strong>
      <button id="clearFiltersBtn" type="button" style="padding:7px 10px;">Clear Filters</button>
    </div>
    <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(150px, 1fr)); gap:8px; margin-top:10px;">
      <select id="filterYear" style="width:100%;"><option value="">Year</option></select>
      <select id="filterGenre" style="width:100%;"><option value="">Genre</option></select>
      <select id="filterActress" style="width:100%;"><option value="">Actress</option></select>
      <select id="filterStudio" style="width:100%;"><option value="">Studio</option></select>
      <select id="filterDuration" style="width:100%;">
        <option value="">Duration</option>
        <option value="short">Under 90 min</option>
        <option value="mid">90-150 min</option>
        <option value="long">150+ min</option>
        <option value="unknown">Unknown</option>
      </select>
      <select id="filterRating" style="width:100%;">
        <option value="">Rating</option>
        <option value="high">4.0+</option>
        <option value="mid">3.0-3.9</option>
        <option value="low">Below 3.0</option>
        <option value="unrated">Unrated</option>
      </select>
    </div>
    <div id="activeFilters" style="display:flex; flex-wrap:wrap; gap:6px; margin-top:10px;"></div>
    <div id="quickChips" style="display:flex; flex-wrap:wrap; gap:6px; margin-top:10px;"></div>
  </section>

  <section id="rails" style="margin-top:14px;"></section>

  <section class="panel" style="margin-top:14px;">
    <div class="section-head">
      <div>
        <strong>All Titles</strong>
        <p class="hint" style="margin:6px 0 0;">Use the dedicated catalog page for advanced filtering and sorting.</p>
      </div>
      <a href="/all-titles" class="action-link">Go to All Titles</a>
    </div>
  </section>
""",
    """
  <script>
    const railsEl = document.getElementById("rails");
    const searchInput = document.getElementById("searchInput");
    const heroPosterEl = document.getElementById("heroPoster");
    const heroJavBadgeEl = document.getElementById("heroJavBadge");
    const heroTitleEl = document.getElementById("heroTitle");
    const heroMetaEl = document.getElementById("heroMeta");
    const heroPlayEl = document.getElementById("heroPlay");
    const heroInfoEl = document.getElementById("heroInfo");
    const filterYearEl = document.getElementById("filterYear");
    const filterGenreEl = document.getElementById("filterGenre");
    const filterActressEl = document.getElementById("filterActress");
    const filterStudioEl = document.getElementById("filterStudio");
    const filterDurationEl = document.getElementById("filterDuration");
    const filterRatingEl = document.getElementById("filterRating");
    const activeFiltersEl = document.getElementById("activeFilters");
    const quickChipsEl = document.getElementById("quickChips");
    const clearFiltersBtn = document.getElementById("clearFiltersBtn");

    let allVideos = [];
    let filteredVideos = [];
    let filterTimer = null;
    const filters = {
      year: "",
      genre: "",
      actress: "",
      studio: "",
      duration: "",
      rating: "",
    };

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

    function parseYear(v) {
      const value = String(v.release_date || "");
      const year = value.slice(0, 4);
      return /^\\d{4}$/.test(year) ? year : "";
    }

    function hasFacet(videoList, key, value) {
      return videoList.some((v) => {
        if (key === "genre") return (v.genres || []).includes(value);
        if (key === "actress") return (v.actresses || []).includes(value);
        if (key === "studio") return (v.publisher || "") === value;
        if (key === "year") return parseYear(v) === value;
        return false;
      });
    }

    function fillSelect(selectEl, options, label) {
      if (!selectEl) return;
      const current = selectEl.value;
      selectEl.innerHTML = "";
      const first = document.createElement("option");
      first.value = "";
      first.textContent = label;
      selectEl.appendChild(first);
      for (const opt of options) {
        const o = document.createElement("option");
        o.value = opt;
        o.textContent = opt;
        selectEl.appendChild(o);
      }
      if ([...selectEl.options].some((o) => o.value === current)) {
        selectEl.value = current;
      } else {
        selectEl.value = "";
      }
    }

    function topValues(items, limit = 24) {
      const count = new Map();
      for (const item of items) {
        count.set(item, (count.get(item) || 0) + 1);
      }
      return [...count.entries()]
        .sort((a, b) => (b[1] - a[1]) || a[0].localeCompare(b[0]))
        .slice(0, limit)
        .map((x) => x[0]);
    }

    function fuzzySubsequenceScore(text, query) {
      if (!text || !query) return 0;
      let qi = 0;
      let run = 0;
      let bonus = 0;
      const source = text.toLowerCase();
      for (let i = 0; i < source.length && qi < query.length; i++) {
        if (source[i] === query[qi]) {
          qi += 1;
          run += 1;
          bonus += run * 0.4;
        } else {
          run = 0;
        }
      }
      if (qi < query.length) return 0;
      return qi + bonus;
    }

    function fuzzyScore(video, query) {
      if (!query) return 1000;
      const q = query.toLowerCase();
      const fields = [
        video.jav_id || "",
        video.title || "",
        video.publisher || "",
        ...(video.actresses || []),
        ...(video.genres || []),
      ];
      let best = 0;
      for (const raw of fields) {
        const text = String(raw || "").toLowerCase();
        if (!text) continue;
        if (text === q) best = Math.max(best, 100);
        else if (text.startsWith(q)) best = Math.max(best, 60);
        else if (text.includes(q)) best = Math.max(best, 40 + Math.min(q.length, 18));
        else best = Math.max(best, fuzzySubsequenceScore(text, q));
      }
      return best;
    }

    function matchDuration(video, bucket) {
      if (!bucket) return true;
      const d = safeNumber(video.duration_min, 0);
      if (!d) return bucket === "unknown";
      if (bucket === "short") return d < 90;
      if (bucket === "mid") return d >= 90 && d < 150;
      if (bucket === "long") return d >= 150;
      return true;
    }

    function matchRating(video, bucket) {
      if (!bucket) return true;
      const r = Number(video.rating);
      if (!Number.isFinite(r)) return bucket === "unrated";
      if (bucket === "high") return r >= 4;
      if (bucket === "mid") return r >= 3 && r < 4;
      if (bucket === "low") return r < 3;
      return true;
    }

    function matchesFacets(video) {
      if (filters.year && parseYear(video) !== filters.year) return false;
      if (filters.genre && !(video.genres || []).includes(filters.genre)) return false;
      if (filters.actress && !(video.actresses || []).includes(filters.actress)) return false;
      if (filters.studio && (video.publisher || "") !== filters.studio) return false;
      if (!matchDuration(video, filters.duration)) return false;
      if (!matchRating(video, filters.rating)) return false;
      return true;
    }

    function isAnyFacetActive() {
      return Object.values(filters).some((v) => !!v);
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
      if (window.matchMedia("(hover: none)").matches) return;
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

    function buildRail(name, items) {
      const section = document.createElement("section");
      section.className = "panel";
      section.style.marginBottom = "14px";
      section.innerHTML = `
        <div style="display:flex; align-items:center; justify-content:space-between; gap:10px; margin-bottom:10px;">
          <strong>${escapeHtml(name)}</strong>
        </div>
        <div data-rail-track style="display:grid; grid-template-columns:repeat(auto-fill, minmax(220px, 1fr)); gap:12px;"></div>
      `;
      const scroller = section.querySelector("[data-rail-track]");
      for (const video of items) {
        scroller.appendChild(makeCard(video));
      }
      return section;
    }

    function buildRails(videos) {
      railsEl.innerHTML = "";
      if (!videos.length) {
        railsEl.innerHTML = '<section class="panel"><div class="empty-state">No videos match this discovery filter set.</div></section>';
        return;
      }

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
      if (!railsEl.children.length) {
        railsEl.innerHTML = '<section class="panel"><div class="empty-state">No recommendation rails available yet.</div></section>';
      }
    }

    function renderActiveFilters() {
      if (!activeFiltersEl) return;
      activeFiltersEl.innerHTML = "";
      const entries = [
        ["year", filters.year],
        ["genre", filters.genre],
        ["actress", filters.actress],
        ["studio", filters.studio],
        ["duration", filters.duration],
        ["rating", filters.rating],
      ].filter(([, value]) => !!value);
      if (!entries.length) {
        activeFiltersEl.innerHTML = '<span class="hint">No active filters.</span>';
        return;
      }
      for (const [key, value] of entries) {
        const chip = document.createElement("button");
        chip.type = "button";
        chip.className = "chip";
        chip.textContent = key + ": " + value + "  ×";
        chip.addEventListener("click", () => {
          filters[key] = "";
          syncFilterControls();
          applyFilter();
        });
        activeFiltersEl.appendChild(chip);
      }
    }

    function updateFacetOptions(sourceVideos) {
      const years = [...new Set(sourceVideos.map(parseYear).filter(Boolean))].sort((a, b) => b.localeCompare(a));
      const genres = topValues(sourceVideos.flatMap((v) => (v.genres || []).filter(Boolean)), 36);
      const actresses = topValues(sourceVideos.flatMap((v) => (v.actresses || []).filter(Boolean)), 36);
      const studios = topValues(sourceVideos.map((v) => v.publisher || "").filter(Boolean), 28);

      fillSelect(filterYearEl, years, "Year");
      fillSelect(filterGenreEl, genres, "Genre");
      fillSelect(filterActressEl, actresses, "Actress");
      fillSelect(filterStudioEl, studios, "Studio");
    }

    function renderQuickChips(videos) {
      if (!quickChipsEl) return;
      quickChipsEl.innerHTML = "";
      const chips = [];
      if (filters.genre && hasFacet(videos, "genre", filters.genre)) {
        chips.push({label: "Genre: " + filters.genre, key: "genre", value: filters.genre});
      } else {
        const topGenre = topValues(videos.flatMap((v) => v.genres || []), 1)[0];
        if (topGenre) chips.push({label: "Top Genre: " + topGenre, key: "genre", value: topGenre});
      }
      const resume = videos.find((v) => safeNumber(v.progress_percent, 0) >= 3 && safeNumber(v.progress_percent, 0) < 96);
      if (resume) chips.push({label: "Resume Ready", key: "resume", value: "resume"});
      const unrated = videos.find((v) => !Number.isFinite(Number(v.rating)));
      if (unrated) chips.push({label: "Unrated", key: "rating", value: "unrated"});
      const longForm = videos.find((v) => safeNumber(v.duration_min, 0) >= 150);
      if (longForm) chips.push({label: "Long Watch", key: "duration", value: "long"});
      const topActress = topValues(videos.flatMap((v) => v.actresses || []), 1)[0];
      if (topActress) chips.push({label: "Actress: " + topActress, key: "actress", value: topActress});
      const topStudio = topValues(videos.map((v) => v.publisher || "").filter(Boolean), 1)[0];
      if (topStudio) chips.push({label: "Studio: " + topStudio, key: "studio", value: topStudio});

      for (const chipInfo of chips.slice(0, 8)) {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "chip";
        btn.textContent = chipInfo.label;
        btn.addEventListener("click", () => {
          if (chipInfo.key === "resume") {
            searchInput.value = "";
            filteredVideos = allVideos.filter((v) => safeNumber(v.progress_percent, 0) >= 3 && safeNumber(v.progress_percent, 0) < 96);
            renderHero(pickFeatured(filteredVideos));
            buildRails(filteredVideos);
            return;
          }
          filters[chipInfo.key] = chipInfo.value;
          syncFilterControls();
          applyFilter();
        });
        quickChipsEl.appendChild(btn);
      }
    }

    function syncFilterControls() {
      if (filterYearEl) filterYearEl.value = filters.year;
      if (filterGenreEl) filterGenreEl.value = filters.genre;
      if (filterActressEl) filterActressEl.value = filters.actress;
      if (filterStudioEl) filterStudioEl.value = filters.studio;
      if (filterDurationEl) filterDurationEl.value = filters.duration;
      if (filterRatingEl) filterRatingEl.value = filters.rating;
    }

    function applyFilter() {
      const query = searchInput.value.trim().toLowerCase();
      const usedFacets = isAnyFacetActive();

      const ranked = allVideos
        .map((v) => ({v, score: fuzzyScore(v, query)}))
        .filter((entry) => entry.score > 0)
        .filter((entry) => matchesFacets(entry.v))
        .sort((a, b) => {
          const scoreDiff = b.score - a.score;
          if (scoreDiff) return scoreDiff;
          return safeNumber(b.v.recommendation_score, 0) - safeNumber(a.v.recommendation_score, 0);
        });
      filteredVideos = ranked.map((entry) => entry.v);

      renderHero(pickFeatured(filteredVideos));
      buildRails(filteredVideos);
      updateFacetOptions(query || usedFacets ? filteredVideos : allVideos);
      renderActiveFilters();
      renderQuickChips(filteredVideos.length ? filteredVideos : allVideos);
    }

    async function init() {
      allVideos = await get("/api/videos");
      updateFacetOptions(allVideos);
      renderHero(pickFeatured(allVideos));
      buildRails(allVideos);
      renderActiveFilters();
      renderQuickChips(allVideos);
    }

    searchInput.addEventListener("input", () => {
      if (filterTimer) window.clearTimeout(filterTimer);
      filterTimer = window.setTimeout(applyFilter, 140);
    });
    if (filterYearEl) {
      filterYearEl.addEventListener("change", () => {
        filters.year = filterYearEl.value;
        applyFilter();
      });
    }
    if (filterGenreEl) {
      filterGenreEl.addEventListener("change", () => {
        filters.genre = filterGenreEl.value;
        applyFilter();
      });
    }
    if (filterActressEl) {
      filterActressEl.addEventListener("change", () => {
        filters.actress = filterActressEl.value;
        applyFilter();
      });
    }
    if (filterStudioEl) {
      filterStudioEl.addEventListener("change", () => {
        filters.studio = filterStudioEl.value;
        applyFilter();
      });
    }
    if (filterDurationEl) {
      filterDurationEl.addEventListener("change", () => {
        filters.duration = filterDurationEl.value;
        applyFilter();
      });
    }
    if (filterRatingEl) {
      filterRatingEl.addEventListener("change", () => {
        filters.rating = filterRatingEl.value;
        applyFilter();
      });
    }
    if (clearFiltersBtn) {
      clearFiltersBtn.addEventListener("click", () => {
        searchInput.value = "";
        filters.year = "";
        filters.genre = "";
        filters.actress = "";
        filters.studio = "";
        filters.duration = "";
        filters.rating = "";
        syncFilterControls();
        applyFilter();
      });
    }
    init().catch((error) => {
      railsEl.innerHTML = '<section class="panel"><p class="hint">Failed to load catalog: ' + error.message + '</p></section>';
    });
  </script>
""",
)


ALL_TITLES_HTML = _layout(
    "All Titles",
    "titles",
    """
  <section class="panel">
    <div class="page-head" style="align-items:flex-start;">
      <div>
        <p class="page-kicker">Catalog</p>
        <h1 class="page-title" style="margin-top:6px;">All Titles</h1>
      </div>
      <div style="display:flex; gap:8px; flex-wrap:wrap;">
        <input id="searchInput" type="search" placeholder="Search by JAV ID, title, actress, genre" style="min-width:300px; max-width:520px; width:100%; background:#12263b; border-color:#426486;" />
        <a href="/view" class="action-link">Back to Browse</a>
      </div>
    </div>
  </section>

  <section class="panel" style="margin-top:14px;">
    <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(150px, 1fr)); gap:8px;">
      <select id="filterYear"><option value="">Year</option></select>
      <select id="filterGenre"><option value="">Genre</option></select>
      <select id="filterActress"><option value="">Actress</option></select>
      <select id="filterStudio"><option value="">Studio</option></select>
      <select id="filterDuration">
        <option value="">Duration</option>
        <option value="short">Under 90 min</option>
        <option value="mid">90-150 min</option>
        <option value="long">150+ min</option>
        <option value="unknown">Unknown</option>
      </select>
      <select id="filterRating">
        <option value="">Rating</option>
        <option value="high">4.0+</option>
        <option value="mid">3.0-3.9</option>
        <option value="low">Below 3.0</option>
        <option value="unrated">Unrated</option>
      </select>
    </div>
    <div style="display:flex; gap:8px; margin-top:10px; flex-wrap:wrap;">
      <select id="sortBy" style="min-width:160px;">
        <option value="recommended">Sort: Recommended</option>
        <option value="newest">Sort: Newest</option>
        <option value="oldest">Sort: Oldest</option>
        <option value="rating">Sort: Rating</option>
        <option value="progress">Sort: Progress</option>
        <option value="title">Sort: Title</option>
      </select>
      <button id="sortDirBtn" type="button">Descending</button>
      <button id="clearFiltersBtn" type="button">Clear Filters</button>
    </div>
    <div id="activeFilters" style="display:flex; flex-wrap:wrap; gap:6px; margin-top:10px;"></div>
  </section>

  <section class="panel" style="margin-top:14px;">
    <div class="section-head">
      <strong>All Titles</strong>
      <span class="stat-pill" id="resultCount"></span>
    </div>
    <div id="grid" style="display:grid; grid-template-columns:repeat(auto-fill, minmax(240px, 280px)); justify-content:start; gap:14px;"></div>
  </section>
""",
    """
  <script>
    const gridEl = document.getElementById("grid");
    const resultCountEl = document.getElementById("resultCount");
    const searchInput = document.getElementById("searchInput");
    const filterYearEl = document.getElementById("filterYear");
    const filterGenreEl = document.getElementById("filterGenre");
    const filterActressEl = document.getElementById("filterActress");
    const filterStudioEl = document.getElementById("filterStudio");
    const filterDurationEl = document.getElementById("filterDuration");
    const filterRatingEl = document.getElementById("filterRating");
    const activeFiltersEl = document.getElementById("activeFilters");
    const clearFiltersBtn = document.getElementById("clearFiltersBtn");
    const sortByEl = document.getElementById("sortBy");
    const sortDirBtn = document.getElementById("sortDirBtn");

    let allVideos = [];
    let descending = true;
    let filterTimer = null;
    const filters = {
      year: "",
      genre: "",
      actress: "",
      studio: "",
      duration: "",
      rating: "",
    };

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

    function safeNumber(value, fallback = 0) {
      const n = Number(value);
      return Number.isFinite(n) ? n : fallback;
    }

    function parseYear(v) {
      const value = String(v.release_date || "");
      const year = value.slice(0, 4);
      return /^\\d{4}$/.test(year) ? year : "";
    }

    function topValues(items, limit = 24) {
      const count = new Map();
      for (const item of items) {
        count.set(item, (count.get(item) || 0) + 1);
      }
      return [...count.entries()]
        .sort((a, b) => (b[1] - a[1]) || a[0].localeCompare(b[0]))
        .slice(0, limit)
        .map((x) => x[0]);
    }

    function fillSelect(selectEl, options, label) {
      const current = selectEl.value;
      selectEl.innerHTML = "";
      const first = document.createElement("option");
      first.value = "";
      first.textContent = label;
      selectEl.appendChild(first);
      for (const opt of options) {
        const o = document.createElement("option");
        o.value = opt;
        o.textContent = opt;
        selectEl.appendChild(o);
      }
      if ([...selectEl.options].some((o) => o.value === current)) {
        selectEl.value = current;
      } else {
        selectEl.value = "";
      }
    }

    function fuzzySubsequenceScore(text, query) {
      if (!text || !query) return 0;
      let qi = 0;
      let run = 0;
      let bonus = 0;
      const source = text.toLowerCase();
      for (let i = 0; i < source.length && qi < query.length; i++) {
        if (source[i] === query[qi]) {
          qi += 1;
          run += 1;
          bonus += run * 0.4;
        } else {
          run = 0;
        }
      }
      if (qi < query.length) return 0;
      return qi + bonus;
    }

    function fuzzyScore(video, query) {
      if (!query) return 1000;
      const q = query.toLowerCase();
      const fields = [
        video.jav_id || "",
        video.title || "",
        video.publisher || "",
        ...(video.actresses || []),
        ...(video.genres || []),
      ];
      let best = 0;
      for (const raw of fields) {
        const text = String(raw || "").toLowerCase();
        if (!text) continue;
        if (text === q) best = Math.max(best, 100);
        else if (text.startsWith(q)) best = Math.max(best, 60);
        else if (text.includes(q)) best = Math.max(best, 40 + Math.min(q.length, 18));
        else best = Math.max(best, fuzzySubsequenceScore(text, q));
      }
      return best;
    }

    function matchDuration(video, bucket) {
      if (!bucket) return true;
      const d = safeNumber(video.duration_min, 0);
      if (!d) return bucket === "unknown";
      if (bucket === "short") return d < 90;
      if (bucket === "mid") return d >= 90 && d < 150;
      if (bucket === "long") return d >= 150;
      return true;
    }

    function matchRating(video, bucket) {
      if (!bucket) return true;
      const r = Number(video.rating);
      if (!Number.isFinite(r)) return bucket === "unrated";
      if (bucket === "high") return r >= 4;
      if (bucket === "mid") return r >= 3 && r < 4;
      if (bucket === "low") return r < 3;
      return true;
    }

    function matchesFacets(video) {
      if (filters.year && parseYear(video) !== filters.year) return false;
      if (filters.genre && !(video.genres || []).includes(filters.genre)) return false;
      if (filters.actress && !(video.actresses || []).includes(filters.actress)) return false;
      if (filters.studio && (video.publisher || "") !== filters.studio) return false;
      if (!matchDuration(video, filters.duration)) return false;
      if (!matchRating(video, filters.rating)) return false;
      return true;
    }

    function updateFacetOptions(sourceVideos) {
      const years = [...new Set(sourceVideos.map(parseYear).filter(Boolean))].sort((a, b) => b.localeCompare(a));
      const genres = topValues(sourceVideos.flatMap((v) => (v.genres || []).filter(Boolean)), 36);
      const actresses = topValues(sourceVideos.flatMap((v) => (v.actresses || []).filter(Boolean)), 36);
      const studios = topValues(sourceVideos.map((v) => v.publisher || "").filter(Boolean), 28);
      fillSelect(filterYearEl, years, "Year");
      fillSelect(filterGenreEl, genres, "Genre");
      fillSelect(filterActressEl, actresses, "Actress");
      fillSelect(filterStudioEl, studios, "Studio");
    }

    function renderActiveFilters() {
      activeFiltersEl.innerHTML = "";
      const entries = [
        ["year", filters.year],
        ["genre", filters.genre],
        ["actress", filters.actress],
        ["studio", filters.studio],
        ["duration", filters.duration],
        ["rating", filters.rating],
      ].filter(([, value]) => !!value);
      if (!entries.length) {
        activeFiltersEl.innerHTML = '<span class="hint">No active filters.</span>';
        return;
      }
      for (const [key, value] of entries) {
        const chip = document.createElement("button");
        chip.type = "button";
        chip.className = "chip";
        chip.textContent = key + ": " + value + "  ×";
        chip.addEventListener("click", () => {
          filters[key] = "";
          syncFilterControls();
          applyFilter();
        });
        activeFiltersEl.appendChild(chip);
      }
    }

    function formatDuration(sec) {
      const total = Math.max(0, Math.floor(safeNumber(sec, 0)));
      const h = Math.floor(total / 3600);
      const m = Math.floor((total % 3600) / 60);
      const s = total % 60;
      if (h > 0) return `${h}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
      return `${m}:${String(s).padStart(2, "0")}`;
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
      if (window.matchMedia("(hover: none)").matches) return;
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

    function renderGrid(videos) {
      gridEl.innerHTML = "";
      resultCountEl.textContent = videos.length + " of " + allVideos.length + " title(s)";
      if (!videos.length) {
        gridEl.innerHTML = '<div class="empty-state">No titles match your current filters. Try clearing one or two filters.</div>';
        return;
      }
      for (const v of videos) {
        const card = document.createElement("a");
        card.className = "card";
        card.href = "/video/" + encodeURIComponent(v.jav_id);
        card.innerHTML = cardMarkup(v);
        attachCardEffects(card);
        gridEl.appendChild(card);
      }
    }

    function compareVideos(a, b) {
      const sortBy = sortByEl.value;
      if (sortBy === "newest") return (b.release_date || "").localeCompare(a.release_date || "");
      if (sortBy === "oldest") return (a.release_date || "").localeCompare(b.release_date || "");
      if (sortBy === "rating") return safeNumber(b.rating, -1) - safeNumber(a.rating, -1);
      if (sortBy === "progress") return safeNumber(b.progress_percent, 0) - safeNumber(a.progress_percent, 0);
      if (sortBy === "title") return (a.title || a.jav_id || "").localeCompare(b.title || b.jav_id || "");
      return safeNumber(b.recommendation_score, 0) - safeNumber(a.recommendation_score, 0);
    }

    function syncFilterControls() {
      filterYearEl.value = filters.year;
      filterGenreEl.value = filters.genre;
      filterActressEl.value = filters.actress;
      filterStudioEl.value = filters.studio;
      filterDurationEl.value = filters.duration;
      filterRatingEl.value = filters.rating;
    }

    function applyFilter() {
      const query = searchInput.value.trim().toLowerCase();
      const source = allVideos
        .map((v) => ({v, score: fuzzyScore(v, query)}))
        .filter((entry) => entry.score > 0)
        .filter((entry) => matchesFacets(entry.v))
        .sort((a, b) => {
          const scoreDiff = b.score - a.score;
          if (scoreDiff) return scoreDiff;
          return compareVideos(a.v, b.v);
        })
        .map((entry) => entry.v);
      source.sort(compareVideos);
      const out = descending ? source : [...source].reverse();
      renderGrid(out);
      updateFacetOptions(query ? out : allVideos);
      renderActiveFilters();
    }

    async function init() {
      allVideos = await get("/api/videos");
      updateFacetOptions(allVideos);
      renderActiveFilters();
      renderGrid(allVideos.sort(compareVideos));
    }

    searchInput.addEventListener("input", () => {
      if (filterTimer) window.clearTimeout(filterTimer);
      filterTimer = window.setTimeout(applyFilter, 140);
    });
    filterYearEl.addEventListener("change", () => { filters.year = filterYearEl.value; applyFilter(); });
    filterGenreEl.addEventListener("change", () => { filters.genre = filterGenreEl.value; applyFilter(); });
    filterActressEl.addEventListener("change", () => { filters.actress = filterActressEl.value; applyFilter(); });
    filterStudioEl.addEventListener("change", () => { filters.studio = filterStudioEl.value; applyFilter(); });
    filterDurationEl.addEventListener("change", () => { filters.duration = filterDurationEl.value; applyFilter(); });
    filterRatingEl.addEventListener("change", () => { filters.rating = filterRatingEl.value; applyFilter(); });
    sortByEl.addEventListener("change", applyFilter);
    sortDirBtn.addEventListener("click", () => {
      descending = !descending;
      sortDirBtn.textContent = descending ? "Descending" : "Ascending";
      applyFilter();
    });
    clearFiltersBtn.addEventListener("click", () => {
      searchInput.value = "";
      filters.year = "";
      filters.genre = "";
      filters.actress = "";
      filters.studio = "";
      filters.duration = "";
      filters.rating = "";
      syncFilterControls();
      applyFilter();
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
            <a id="theaterLink" href="/watch/__JAV_ID__" class="action-link" style="color:#ffdcb8; border-color:rgba(249, 115, 22, 0.52); background:rgba(249, 115, 22, 0.1);">Open Theater</a>
            <a href="/view" class="action-link">Back to Browse</a>
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
    <div id="watchGrid" style="display:grid; grid-template-columns:minmax(0, 2.4fr) minmax(300px, 1fr);">
      <div id="watchMain" style="padding:18px; border-right:1px solid rgba(58, 95, 127, 0.55);">
        <p class="page-kicker" style="margin:0;">Now Playing</p>
        <h1 id="watchTitle" class="page-title" style="margin-top:7px;">__JAV_ID__</h1>
        <p id="watchMeta" style="margin:9px 0 0; color:#bdd8f2; font-size:14px;"></p>
        <div id="resumeBox" style="display:none; margin-top:10px; gap:8px; flex-wrap:wrap;">
          <button id="resumeBtn" type="button" class="primary" style="padding:8px 12px;">Resume</button>
          <button id="restartBtn" type="button" style="padding:8px 12px;">Start Over</button>
          <span id="resumeText" class="hint"></span>
        </div>

        <div style="margin-top:14px; border:1px solid #304e6b; border-radius:14px; overflow:hidden; background:#05070c; box-shadow:0 16px 34px rgba(0,0,0,.38);">
          <video id="watchPlayer" controls autoplay playsinline src="/api/local-video?id=__JAV_ID__" style="width:100%; max-height:78vh; display:block; background:#000;"></video>
        </div>
        <p class="hint" style="margin:10px 0 0;">Keyboard: left/right seeks, space toggles play/pause.</p>
      </div>

      <aside style="padding:18px; display:grid; align-content:start; gap:12px; background:rgba(8, 18, 31, 0.55);">
        <div>
          <h2 style="margin:0; font-size:18px;">Navigation</h2>
          <p class="hint" style="margin:6px 0 0;">Playback stays primary. Use these when you need context.</p>
        </div>
        <div class="watch-actions" style="display:grid; gap:8px;">
          <a href="/video/__JAV_ID__" class="action-link">Open Details</a>
          <a href="/view" class="action-link">Back to Browse</a>
        </div>

        <div class="panel panel-muted">
          <div style="display:flex; justify-content:space-between; align-items:center; gap:8px;">
            <p class="fact-label" style="margin:0;">Up Next</p>
            <a href="/view" class="hint" style="font-size:12px;">See all</a>
          </div>
          <div id="upNextList" style="display:grid; gap:8px; margin-top:8px;"></div>
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

    function escapeHtml(text) {
      return (text || "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;");
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
    const upNextList = document.getElementById("upNextList");

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

    function renderUpNext(items) {
      if (!upNextList) return;
      upNextList.innerHTML = "";
      const list = Array.isArray(items) ? items : [];
      if (!list.length) {
        upNextList.innerHTML = '<p class="hint" style="margin:0;">No recommendations yet.</p>';
        return;
      }
      for (const item of list.slice(0, 8)) {
        const p = Math.max(0, Math.min(100, safeNumber(item.progress_percent, 0)));
        const title = item.title || item.jav_id;
        const row = document.createElement("a");
        row.href = "/watch/" + encodeURIComponent(item.jav_id);
        row.style.textDecoration = "none";
        row.style.display = "grid";
        row.style.gridTemplateColumns = "92px minmax(0, 1fr)";
        row.style.gap = "8px";
        row.style.border = "1px solid #4d6c8d";
        row.style.background = "rgba(16, 33, 50, 0.9)";
        row.style.borderRadius = "12px";
        row.style.overflow = "hidden";
        row.innerHTML = `
          <img src="${item.poster_url}" alt="${escapeHtml(item.jav_id)}" loading="lazy" style="width:100%; height:100%; min-height:56px; object-fit:cover; display:block;" />
          <div style="padding:7px 8px;">
            <div style="font-weight:700; font-size:12px; color:#e8f4ff; line-height:1.3;">${escapeHtml(item.jav_id)}</div>
            <div class="hint" style="font-size:11px; margin-top:2px; line-height:1.35; color:#c2d8ee;">${escapeHtml(title)}</div>
            <div style="margin-top:6px; height:3px; width:100%; border-radius:999px; overflow:hidden; background:rgba(191, 219, 254, 0.2);">
              <div style="height:100%; width:${p}%; background:linear-gradient(90deg, #22d3ee, #14b8a6);"></div>
            </div>
          </div>
        `;
        upNextList.appendChild(row);
      }
    }

    async function loadUpNext() {
      try {
        const rows = await get("/api/recommendations?id=__JAV_ID__&limit=8");
        renderUpNext(rows);
      } catch (error) {
        if (upNextList) {
          upNextList.innerHTML = '<p class="hint" style="margin:0;">Failed to load recommendations.</p>';
        }
      }
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
    loadUpNext();
  </script>
""",
)
