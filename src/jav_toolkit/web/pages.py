from __future__ import annotations


def _layout(title: str, active: str, content: str, script: str = "") -> str:
    nav_links = [
        ("organize", "/organize", "Organize"),
        ("view", "/view", "View"),
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
      --bg: #05070e;
      --bg-2: #0b1120;
      --panel: #0f1727;
      --panel-2: #111d30;
      --ink: #e6edf8;
      --muted: #90a0bf;
      --line: #22304b;
      --brand: #e11d48;
      --brand-2: #be123c;
      --chip: #17243a;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      color: var(--ink);
      font-family: "Poppins", "Avenir Next", "Segoe UI", sans-serif;
      background:
        radial-gradient(circle at 8% -2%, rgba(57, 86, 164, 0.27) 0, transparent 37%),
        radial-gradient(circle at 94% 10%, rgba(225, 29, 72, 0.2) 0, transparent 35%),
        linear-gradient(180deg, var(--bg), var(--bg-2));
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }}
    a {{ color: inherit; }}
    .shell {{ max-width: 1320px; margin: 0 auto; width: 100%; padding: 18px 20px 26px; }}
    .navbar {{
      position: sticky;
      top: 0;
      z-index: 20;
      backdrop-filter: blur(10px);
      background: rgba(7, 12, 25, 0.72);
      border-bottom: 1px solid rgba(34, 48, 75, 0.95);
    }}
    .nav-inner {{
      max-width: 1320px;
      margin: 0 auto;
      padding: 10px 20px;
      display: flex;
      gap: 10px;
      align-items: center;
      justify-content: space-between;
    }}
    .brand {{
      font-size: 13px;
      font-weight: 700;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      text-decoration: none;
      color: #f6f9ff;
    }}
    .nav-links {{ display: flex; gap: 8px; align-items: center; }}
    .nav-link {{
      text-decoration: none;
      padding: 8px 10px;
      border-radius: 999px;
      border: 1px solid transparent;
      color: var(--muted);
      font-size: 13px;
      background: transparent;
    }}
    .nav-link:hover {{ border-color: var(--line); color: var(--ink); background: rgba(255,255,255,0.06); }}
    .nav-link.active {{
      background: var(--brand);
      color: #fff;
      border-color: var(--brand);
    }}
    .panel {{
      background: linear-gradient(180deg, var(--panel), var(--panel-2));
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 16px;
      box-shadow: 0 12px 30px rgba(2, 8, 20, 0.33);
    }}
    .footer {{
      margin-top: auto;
      border-top: 1px solid var(--line);
      color: var(--muted);
      font-size: 12px;
      background: rgba(5, 8, 16, 0.45);
    }}
    .footer-inner {{ max-width: 1320px; margin: 0 auto; padding: 10px 20px 14px; }}

    button, input {{
      font: inherit;
      border-radius: 10px;
      border: 1px solid var(--line);
      padding: 10px 12px;
      background: #0d1524;
      color: var(--ink);
    }}
    button {{ cursor: pointer; }}
    button.primary {{ background: var(--brand); color: #fff; border-color: var(--brand); }}
    button.primary:hover {{ background: var(--brand-2); border-color: var(--brand-2); }}
    .hint {{ color: var(--muted); font-size: 13px; }}
    .page-head {{
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      gap: 12px;
      align-items: flex-end;
    }}
    .page-kicker {{
      margin: 0;
      font-size: 11px;
      letter-spacing: .2em;
      text-transform: uppercase;
      color: #9fb1d4;
    }}
    .page-title {{
      margin: 6px 0 0;
      font-size: 30px;
      line-height: 1.1;
    }}
    .card {{
      text-decoration: none;
      color: inherit;
      border: 1px solid var(--line);
      border-radius: 12px;
      background: #0c1525;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
      min-width: 0;
    }}
    .card:hover {{
      transform: translateY(-5px);
      box-shadow: 0 18px 34px rgba(2, 8, 20, 0.45);
      border-color: #395684;
    }}
    .card-thumb {{
      position: relative;
      aspect-ratio: 16 / 9;
      background: #13213a;
      overflow: hidden;
      flex: 0 0 auto;
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
      transition: opacity .2s ease;
    }}
    .card-meta {{
      padding: 10px 12px 12px;
      display: grid;
      gap: 6px;
      min-height: 106px;
      align-content: start;
    }}
    .card-title {{
      font-weight: 700;
      font-size: 14px;
      line-height: 1.3;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
      min-height: calc(1.3em * 2);
    }}
    .card-sub {{
      color: var(--muted);
      font-size: 12px;
      min-height: calc(1.25em * 2);
    }}
    .pill {{
      display: inline-block;
      font-size: 11px;
      border-radius: 999px;
      background: var(--chip);
      color: #bdd2f7;
      border: 1px solid #2c3f63;
      padding: 2px 8px;
      width: fit-content;
    }}
    .fact-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 8px 12px;
    }}
    .fact {{
      background: #0b1527;
      border: 1px solid #273b5b;
      border-radius: 10px;
      padding: 8px 10px;
    }}
    .fact-label {{
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: .08em;
      color: #90a8d0;
      margin: 0 0 4px;
    }}
    .fact-value {{
      font-size: 13px;
      color: #e1eaff;
      word-break: break-word;
    }}
    .chip-list {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
    }}
    .chip {{
      font-size: 12px;
      border: 1px solid #2b3e60;
      background: #111d31;
      color: #cfe0ff;
      border-radius: 999px;
      padding: 4px 9px;
    }}
    .plot {{
      margin: 0;
      font-size: 13px;
      line-height: 1.5;
      color: #cad8f2;
      white-space: pre-wrap;
    }}

    @media (max-width: 1020px) {{
      #heroSection {{ grid-template-columns: 1fr !important; }}
      #heroPoster {{ min-height: 220px !important; max-height: 340px; }}
      #searchInput {{ max-width: none !important; }}
      .detail-layout {{ grid-template-columns: 1fr !important; }}
      .detail-poster-wrap {{ max-width: none; }}
      .fact-grid {{ grid-template-columns: 1fr; }}
    }}

    @media (max-width: 760px) {{
      .shell {{ padding: 14px 12px 18px; }}
      .nav-inner {{ padding: 10px 12px; }}
      .nav-links {{ gap: 6px; }}
      .nav-link {{ padding: 7px 9px; font-size: 13px; }}
      .brand {{ font-size: 12px; letter-spacing: 0.1em; }}

      #manualPath {{ min-width: 0 !important; width: 100% !important; }}
      #chooseBtn, #manualBtn, #processBtn {{ width: 100%; }}

      .page-title {{ font-size: 24px; }}
      #heroTitle {{ font-size: 22px !important; }}
      #heroMeta {{ font-size: 13px !important; }}
      #grid {{ grid-template-columns: repeat(auto-fill, minmax(165px, 1fr)) !important; gap: 10px !important; }}
      #rails .panel {{ padding: 12px; }}
      #rails [aria-label] {{ grid-auto-columns: minmax(210px, 82vw) !important; }}

      #watchTitle {{ font-size: 22px !important; }}
      #watchMeta {{ font-size: 13px !important; }}
      .detail-poster-wrap {{ max-width: none !important; }}
      .detail-actions a, .detail-actions button {{ flex: 1; text-align: center; }}
    }}
  </style>
</head>
<body>
  <header class="navbar">
    <div class="nav-inner">
      <a class="brand" href="/organize">JAV Organizer</a>
      <nav class="nav-links">{nav}</nav>
    </div>
  </header>
  <main class="shell">
    {content}
  </main>
  <footer class="footer">
    <div class="footer-inner">Local-only workflow: scan, process, browse, and play from your own machine.</div>
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
    <div id="logs" style="background:#060b16; color:#bfeadf; font-family:ui-monospace, SFMono-Regular, Menlo, monospace; border-radius:10px; padding:10px; min-height:180px; max-height:220px; overflow:auto; white-space:pre-wrap; font-size:12px;"></div>
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
  <section class="panel" style="background: linear-gradient(120deg, #0f172a, #18243d); color:#e8eefc; border-color:#27344e;">
    <div class="page-head">
      <div>
        <p class="page-kicker">View</p>
        <h1 class="page-title">Your Local Streaming Shelf</h1>
      </div>
      <input id="searchInput" type="search" placeholder="Search by JAV ID or title" style="min-width:280px; max-width:460px; width:100%; background:#111b31; border-color:#304469; color:#eef5ff;" />
    </div>
  </section>

  <section id="hero" class="panel" style="margin-top:14px; background:#0d1426; border-color:#2b3b58; color:#eef4ff; display:none; padding:0; overflow:hidden;">
    <div id="heroSection" style="display:grid; grid-template-columns: minmax(220px, 34%) minmax(0, 1fr);">
      <div style="background:#121d34;">
        <img id="heroPoster" src="" alt="" style="width:100%; height:100%; object-fit:cover; display:block; min-height:260px;" />
      </div>
      <div style="padding:22px;">
        <p style="margin:0; font-size:12px; letter-spacing:.2em; text-transform:uppercase; color:#8ea6cc;">Featured Tonight</p>
        <h2 id="heroTitle" style="margin:8px 0 0; font-size:28px; line-height:1.2;"></h2>
        <p id="heroMeta" style="margin:10px 0 0; color:#b9cbec; font-size:14px;"></p>
        <div style="margin-top:18px; display:flex; gap:10px; flex-wrap:wrap;">
          <a id="heroInfo" href="#" style="text-decoration:none; background:#0f766e; color:#fff; border:1px solid #0f766e; padding:10px 14px; border-radius:10px; font-weight:700;">Open Details</a>
          <a id="heroPlay" href="#" style="text-decoration:none; background:#1c2a45; color:#d6e3fb; border:1px solid #334766; padding:10px 14px; border-radius:10px;">Play Now</a>
        </div>
      </div>
    </div>
  </section>

  <section id="rails" style="margin-top:14px; display:none;"></section>

  <section class="panel" style="margin-top:14px;">
    <div style="display:flex; justify-content:space-between; gap:10px; align-items:center; margin-bottom:10px;">
      <strong>Catalog Grid</strong>
      <span class="hint" id="resultCount"></span>
    </div>
    <div id="grid" style="display:grid; grid-template-columns:repeat(auto-fill, minmax(250px, 1fr)); gap:14px;"></div>
  </section>
""",
    """
  <script>
    const gridEl = document.getElementById("grid");
    const searchInput = document.getElementById("searchInput");
    const resultCount = document.getElementById("resultCount");
    const heroEl = document.getElementById("hero");
    const heroPosterEl = document.getElementById("heroPoster");
    const heroTitleEl = document.getElementById("heroTitle");
    const heroMetaEl = document.getElementById("heroMeta");
    const heroPlayEl = document.getElementById("heroPlay");
    const heroInfoEl = document.getElementById("heroInfo");
    const railsEl = document.getElementById("rails");
    let activeRailScroller = null;
    let allVideos = [];

    async function get(url) {
      const res = await fetch(url);
      if (!res.ok) throw new Error(res.statusText);
      return res.json();
    }

    function escapeHtml(text) {
      return (text || "").replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;");
    }

    function toWatch(v) {
      return "/watch/" + encodeURIComponent(v.jav_id);
    }
    function toDetail(v) {
      return "/video/" + encodeURIComponent(v.jav_id);
    }

    function scoreVideo(v) {
      let score = 0;
      if (v.has_preview_local) score += 3;
      if (v.has_poster_local) score += 2;
      if (v.release_date) score += 1;
      return score;
    }

    function pickFeatured(videos) {
      if (!videos.length) return null;
      return [...videos].sort((a, b) => {
        const s = scoreVideo(b) - scoreVideo(a);
        if (s) return s;
        return (b.release_date || "").localeCompare(a.release_date || "");
      })[0];
    }

    function renderHero(video) {
      if (!video) {
        heroEl.style.display = "none";
        return;
      }
      heroPosterEl.src = video.poster_url;
      heroPosterEl.alt = video.jav_id;
      heroTitleEl.textContent = video.title ? (video.jav_id + " - " + video.title) : video.jav_id;
      heroMetaEl.textContent = [video.release_date || "Unknown date", video.publisher || "Unknown publisher"].join(" / ");
      heroPlayEl.href = toWatch(video);
      heroInfoEl.href = toDetail(video);
      heroEl.style.display = "block";
    }

    function cardMarkup(v) {
      return `
        <div class="card-thumb">
          <img src="${v.poster_url}" alt="${escapeHtml(v.title || "Untitled")}" loading="lazy" style="width:100%; height:100%; object-fit:cover; display:block;" />
          <video muted loop playsinline preload="none" src="${v.preview_url}" style="position:absolute; inset:0; width:100%; height:100%; object-fit:cover; opacity:0; transition:opacity .2s ease;"></video>
          <div style="position:absolute; inset:auto 0 0; padding:6px 8px; font-size:12px; color:#fff; background:linear-gradient(180deg, transparent, rgba(0,0,0,.75));">${escapeHtml(v.jav_id)}</div>
        </div>
        <div class="card-meta">
          <div class="pill">${escapeHtml(v.jav_id)}</div>
          <div class="card-title">${escapeHtml(v.title || "Untitled")}</div>
          <div class="card-sub">${escapeHtml(v.release_date || "-")} ${escapeHtml(v.publisher || "")}</div>
        </div>
      `;
    }

    function attachCardEffects(card) {
      const preview = card.querySelector("video");
      card.addEventListener("mouseenter", () => {
        card.style.transform = "translateY(-4px)";
        card.style.boxShadow = "0 12px 24px rgba(15, 23, 42, .2)";
        preview.style.opacity = "1";
        preview.play().catch(() => {});
      });
      card.addEventListener("mouseleave", () => {
        card.style.transform = "translateY(0)";
        card.style.boxShadow = "none";
        preview.style.opacity = "0";
        preview.pause();
        preview.currentTime = 0;
      });
    }

    function makeCard(v) {
      const card = document.createElement("a");
      card.href = toDetail(v);
      card.className = "card";
      card.innerHTML = cardMarkup(v);
      attachCardEffects(card);
      return card;
    }

    function scrollRail(scroller, direction) {
      if (!scroller) return;
      const amount = Math.max(280, Math.floor(scroller.clientWidth * 0.82));
      scroller.scrollBy({left: amount * direction, behavior: "smooth"});
    }

    function buildRails(videos) {
      railsEl.innerHTML = "";
      activeRailScroller = null;
      if (!videos.length) {
        railsEl.style.display = "none";
        return;
      }

      const rows = [];
      const recent = [...videos]
        .filter((v) => !!v.release_date)
        .sort((a, b) => (b.release_date || "").localeCompare(a.release_date || ""))
        .slice(0, 12);
      if (recent.length) rows.push({name: "Recently Released", items: recent});

      for (const row of rows) {
        const section = document.createElement("section");
        section.className = "panel";
        section.style.marginBottom = "14px";
        const title = document.createElement("div");
        title.style.marginBottom = "10px";
        title.style.display = "flex";
        title.style.alignItems = "center";
        title.style.justifyContent = "space-between";
        title.style.gap = "10px";
        title.innerHTML = `
          <strong>${escapeHtml(row.name)}</strong>
          <div style="display:flex; gap:6px;">
            <button type="button" data-dir="-1" style="padding:6px 10px; min-width:42px;">&#8592;</button>
            <button type="button" data-dir="1" style="padding:6px 10px; min-width:42px;">&#8594;</button>
          </div>
        `;
        const scroller = document.createElement("div");
        scroller.style.display = "grid";
        scroller.style.gridAutoFlow = "column";
        scroller.style.gridAutoColumns = "minmax(230px, 1fr)";
        scroller.style.gap = "12px";
        scroller.style.overflowX = "auto";
        scroller.style.paddingBottom = "6px";
        scroller.tabIndex = 0;
        scroller.style.outline = "none";
        scroller.setAttribute("aria-label", row.name);
        scroller.addEventListener("mouseenter", () => { activeRailScroller = scroller; });
        scroller.addEventListener("focus", () => { activeRailScroller = scroller; });

        for (const v of row.items) {
          scroller.appendChild(makeCard(v));
        }
        const buttons = title.querySelectorAll("button[data-dir]");
        for (const btn of buttons) {
          btn.addEventListener("click", () => {
            const direction = Number(btn.dataset.dir || "0");
            activeRailScroller = scroller;
            scrollRail(scroller, direction);
          });
        }
        section.appendChild(title);
        section.appendChild(scroller);
        railsEl.appendChild(section);
        if (!activeRailScroller) activeRailScroller = scroller;
      }
      railsEl.style.display = rows.length ? "block" : "none";
    }

    function render(videos) {
      gridEl.innerHTML = "";
      resultCount.textContent = videos.length + " title(s)";
      for (const v of videos) {
        gridEl.appendChild(makeCard(v));
      }
    }

    function applyFilter() {
      const q = searchInput.value.trim().toLowerCase();
      if (!q) {
        renderHero(pickFeatured(allVideos));
        buildRails(allVideos);
        render(allVideos);
        return;
      }
      const filtered = allVideos.filter((v) => {
        return (v.jav_id || "").toLowerCase().includes(q) || (v.title || "").toLowerCase().includes(q);
      });
      renderHero(pickFeatured(filtered));
      buildRails(filtered);
      render(filtered);
    }

    async function init() {
      allVideos = await get("/api/videos");
      renderHero(pickFeatured(allVideos));
      buildRails(allVideos);
      render(allVideos);
    }

    searchInput.addEventListener("input", applyFilter);
    document.addEventListener("keydown", (event) => {
      if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") return;
      const tag = (event.target && event.target.tagName) ? event.target.tagName.toLowerCase() : "";
      if (tag === "input" || tag === "textarea") return;
      if (!activeRailScroller) return;
      event.preventDefault();
      scrollRail(activeRailScroller, event.key === "ArrowLeft" ? -1 : 1);
    });
    init().catch((err) => {
      gridEl.innerHTML = '<p class="hint">Failed to load catalog: ' + err.message + '</p>';
    });
  </script>
""",
)


VIDEO_HTML = _layout(
    "Video __JAV_ID__",
    "view",
    """
  <section class="panel" style="background:linear-gradient(120deg, #0d1426, #17243e); color:#ebf2ff; border-color:#2f425f;">
    <div class="page-head">
      <div>
        <p class="page-kicker">Video Details</p>
        <h1 id="detailTitle" class="page-title">__JAV_ID__</h1>
      </div>
      <div class="detail-actions" style="display:flex; gap:10px; flex-wrap:wrap;">
        <button id="detailPlayBtn" type="button" class="primary" style="padding:10px 14px; font-weight:700;">Play Full Video</button>
        <a id="theaterLink" href="/watch/__JAV_ID__" style="text-decoration:none; background:#0f766e; color:#fff; border:1px solid #0f766e; padding:10px 14px; border-radius:10px; font-weight:700;">Open Theater Mode</a>
        <a href="/view" style="text-decoration:none; background:#1c2a45; color:#d6e3fb; border:1px solid #334766; padding:10px 14px; border-radius:10px;">Back to Grid</a>
      </div>
    </div>
    <p id="detailMeta" style="margin:10px 0 0; color:#bed0f0; font-size:14px;"></p>
  </section>

  <section class="detail-layout" style="display:grid; grid-template-columns:minmax(0, 1.8fr) minmax(290px, 1fr); gap:14px; margin-top:14px;">
    <article class="panel detail-poster-wrap" style="padding:0; overflow:hidden; position:relative;">
      <div id="heroMediaWrap" style="position:relative; width:100%; aspect-ratio:16 / 9; background:#050a14;">
        <img id="detailPoster" src="/api/poster?id=__JAV_ID__" alt="__JAV_ID__ poster" style="display:block; width:100%; height:100%; object-fit:cover; background:#0a1120;" />
      </div>
      <div style="position:absolute; inset:auto 12px 12px auto; background:rgba(5,10,20,.72); border:1px solid #2f425f; color:#d8e6ff; border-radius:999px; font-size:11px; padding:4px 8px;">Poster</div>
    </article>
    <article class="panel">
      <h2 style="margin:0; font-size:18px;">Quick Preview</h2>
      <p class="hint" style="margin:8px 0 14px;">Start with preview first. Load full playback only when you want to watch.</p>
      <video id="detailPreview" muted loop autoplay playsinline controls preload="metadata" src="/api/preview?id=__JAV_ID__" style="width:100%; border-radius:10px; background:#000; aspect-ratio:16 / 9;"></video>
      <div style="margin-top:14px; display:grid; gap:8px;">
        <div class="hint"><strong style="color:#cfe0ff;">JAV ID:</strong> __JAV_ID__</div>
        <div class="hint" id="detailStatus">Ready to play full video.</div>
      </div>
    </article>
  </section>

  <section class="panel" style="margin-top:14px;">
    <h2 style="margin:0 0 10px; font-size:18px;">Metadata</h2>
    <div id="detailFacts" class="fact-grid"></div>
    <div style="margin-top:14px;">
      <div class="fact-label">Actresses</div>
      <div id="detailActresses" class="chip-list"></div>
    </div>
    <div style="margin-top:12px;">
      <div class="fact-label">Tags</div>
      <div id="detailGenres" class="chip-list"></div>
    </div>
    <div style="margin-top:12px;">
      <div class="fact-label">Plot</div>
      <p id="detailPlot" class="plot">-</p>
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

    function escapeHtml(text) {
      return (text || "").replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;");
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
        ["Has Local Video", data.has_local_video ? "Yes" : "No", false],
        ["Screenshots", Array.isArray(data.screenshots) ? String(data.screenshots.length) : "0", false],
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

    async function initDetail() {
      try {
        const data = await get("/api/video?id=__JAV_ID__");
        if (!data || !data.jav_id) return;
        const title = data.title ? data.jav_id + " - " + data.title : data.jav_id;
        document.getElementById("detailTitle").textContent = title;
        const bits = [data.release_date || null, data.publisher || null].filter(Boolean);
        document.getElementById("detailMeta").textContent = bits.join(" / ");
        document.getElementById("detailPlot").textContent = data.plot || "-";
        renderChips("detailActresses", data.actresses || []);
        renderChips("detailGenres", data.genres || []);
        renderFacts(data);
        document.title = "Video " + title;
      } catch (err) {
        document.getElementById("detailMeta").textContent = "Metadata unavailable.";
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
      video.style.display = "block";
      video.style.width = "100%";
      video.style.height = "100%";
      video.style.objectFit = "contain";
      video.style.background = "#000";
      wrap.innerHTML = "";
      wrap.appendChild(video);
      wrap.dataset.loaded = "1";
      statusEl.textContent = "Full video loaded in player.";
    }

    document.getElementById("detailPlayBtn").addEventListener("click", loadMainVideo);
    const detailPreview = document.getElementById("detailPreview");
    if (detailPreview) {
      detailPreview.play().catch(() => {});
    }
    initDetail();
  </script>
""",
)


WATCH_HTML = _layout(
    "Watch __JAV_ID__",
    "view",
    """
  <section class="panel" style="background:linear-gradient(120deg, #0d1426, #17243e); color:#ebf2ff; border-color:#2f425f;">
    <div class="page-head">
      <div>
        <p class="page-kicker">Now Playing</p>
        <h1 id="watchTitle" class="page-title">__JAV_ID__</h1>
      </div>
      <div style="display:flex; gap:10px; flex-wrap:wrap;">
        <a href="/video/__JAV_ID__" style="text-decoration:none; background:#1c2a45; color:#d6e3fb; border:1px solid #334766; padding:10px 14px; border-radius:10px;">Video Details</a>
        <a href="/view" style="text-decoration:none; background:#1c2a45; color:#d6e3fb; border:1px solid #334766; padding:10px 14px; border-radius:10px;">Back to Grid</a>
      </div>
    </div>
    <p id="watchMeta" style="margin:6px 0 0; color:#bed0f0; font-size:14px;"></p>
  </section>

  <section class="panel" style="margin-top:14px; background:#070a12; border-color:#1f2c45;">
    <video controls autoplay playsinline src="/api/local-video?id=__JAV_ID__" style="width:100%; max-height:74vh; display:block; background:#000; border-radius:10px;"></video>
  </section>
""",
    """
  <script>
    async function get(url) {
      const res = await fetch(url);
      if (!res.ok) throw new Error(res.statusText);
      return res.json();
    }

    async function initMeta() {
      try {
        const data = await get("/api/video?id=__JAV_ID__");
        if (data && data.jav_id) {
          const title = data.title ? data.jav_id + " - " + data.title : data.jav_id;
          document.getElementById("watchTitle").textContent = title;
          const bits = [data.release_date || null, data.publisher || null].filter(Boolean);
          document.getElementById("watchMeta").textContent = bits.join(" / ");
          document.title = "Watch " + title;
        }
      } catch (err) {
        document.getElementById("watchMeta").textContent = "Metadata unavailable.";
      }
    }

    initMeta();
  </script>
""",
)
