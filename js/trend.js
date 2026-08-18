/* ============================================================
   风向标趋势页：跨榜影响力 / 作者势力 / 分类热度 / 题材 / 榜首变迁
   ============================================================ */
(() => {
  document.querySelector('[data-nav="index"]').innerHTML = I.grid(16) + " 看板";
  document.querySelector('[data-nav="trend"]').innerHTML = I.compass(16) + " 风向标";
  document.getElementById("headIcon").innerHTML = I.compass(21);
  document.getElementById("briefIcon").innerHTML = I.robot(21);
  document.getElementById("xbHead").innerHTML =
    `${I.radar(18)}<h2>跨榜影响力 Top</h2><span class="hint">多榜同时上榜 · 综合动能</span>`;
  document.getElementById("authorHead").innerHTML =
    `${I.trophy(18)}<h2>作者势力榜</h2><span class="hint" id="authorHint"></span>`;
  document.getElementById("heatIcon").innerHTML = I.chart(18);
  document.getElementById("kwIcon").innerHTML = I.tag(18);
  document.getElementById("tlIcon").innerHTML = I.crown(18);
  document.getElementById("stIcon").innerHTML = I.refresh(18);

  const $ = (id) => document.getElementById(id);

  // ---- 日报 ----
  async function loadBrief() {
    try {
      const b = await QT.fetchJSON("api/market-brief.json");
      $("briefLabel").innerHTML =
        `今日起点风向日报 ${b.engine === "AI" ? '<span class="engine-tag">AI 生成</span>' : '<span class="engine-tag">规则引擎</span>'}`;
      $("briefText").textContent = b.brief || "暂无日报。";
    } catch {
      $("briefText").textContent = "日报未生成。";
    }
  }

  // ---- 跨榜影响力 ----
  async function loadCross() {
    try {
      const d = await QT.fetchJSON("api/cross-board.json");
      const rows = (d.top || []).slice(0, 12);
      $("xbTable").innerHTML = rows.map((e, i) => `
        <a class="xb-row" href="book.html?bid=${e.bid}">
          <span class="xb-medal">${i + 1}</span>
          <span>
            <div class="xb-title">${QT.esc(e.title)}
              ${e.isNew ? `<span class="rank-change new" style="margin-left:6px">${I.sparkle(11)} 新入局</span>` : ""}</div>
            <div class="xb-sub">
              <span>${QT.esc(e.author)}</span>
              <span>·</span><span>${QT.esc(e.subCategory || e.category)}</span>
              ${e.boards.slice(0, 4).map(b =>
                `<span class="board-tag">${QT.esc(b.board)} 第${b.rank}</span>`).join("")}
            </div>
          </span>
          <span class="xb-score"><div class="v">${e.momentum}</div><div class="l">动能</div></span>
        </a>`).join("") || `<div class="state-block"><p>暂无跨榜数据</p></div>`;
    } catch {
      $("xbTable").innerHTML = `<div class="state-block"><p>cross-board.json 未构建</p></div>`;
    }
  }

  // ---- 作者势力（跟随看板当前榜单，?board= 切换）----
  async function loadAuthors() {
    const boards = await QT.fetchJSON("api/boards.json").catch(() => ({ boards: [] }));
    const slug = QT.getParam("board") ||
      (boards.boards || []).find(b => b.date)?.slug;
    const bname = (boards.boards || []).find(b => b.slug === slug);
    $("authorHint").textContent = bname ? bname.name : "";
    if (!slug) return;
    try {
      const s = await QT.fetchJSON(`api/${slug}/market_summary.json`);
      const top = (s.author_power || []).slice(0, 10);
      $("authorList").innerHTML = top.map((a, i) => `
        <div class="dark-item">
          <span class="dark-rank ${i < 3 ? "hot" : ""}">${i + 1}</span>
          <span class="dark-info">
            <span class="dark-name">${QT.esc(a.author)}</span>
            <span class="dark-sub">${a.titles.slice(0, 2).map(QT.esc).join(" / ")}</span>
          </span>
          <span class="dark-score">${a.books} 本</span>
        </div>`).join("") ||
        `<div class="state-block"><p>该榜暂无「一书以上在榜」的作者</p></div>`;
    } catch {
      $("authorList").innerHTML = `<div class="state-block"><p>暂无数据</p></div>`;
    }
  }

  // ---- 分类热度 + 题材关键词（默认月票榜，可 ?board= 切换）----
  async function loadHeat() {
    const boards = await QT.fetchJSON("api/boards.json").catch(() => ({ boards: [] }));
    const slug = QT.getParam("board") ||
      (boards.boards || []).find(b => b.date)?.slug;
    if (!slug) return;
    try {
      const s = await QT.fetchJSON(`api/${slug}/market_summary.json`);
      const heats = (s.category_heat || []).filter(h => h.name !== "全部").slice(0, 10);
      const max = Math.max(...heats.map(h => h.heat), 1);
      $("heatHint").textContent = `${(boards.boards || []).find(b => b.slug === slug)?.name || ""} · 按指标总量`;
      $("heatList").innerHTML = heats.map(h => `
        <div class="heat-row">
          <span class="heat-name">${QT.esc(h.name)}</span>
          <span class="heat-bar"><span class="heat-fill" data-w="${(h.heat / max * 100).toFixed(1)}"></span></span>
          <span class="heat-val">${h.metric_total ? QT.fmtNum(h.metric_total) : h.count + " 本"}</span>
        </div>`).join("");
      requestAnimationFrame(() =>
        requestAnimationFrame(() =>
          document.querySelectorAll(".heat-fill").forEach(el =>
            el.style.width = el.dataset.w + "%")));

      const kws = (s.keyword_heat || []).slice(0, 16);
      const kmax = Math.max(...kws.map(k => k.count), 1);
      $("kwCloud").innerHTML = kws.map((k, i) =>
        `<a class="kw ${k.count / kmax > 0.6 ? "hi" : ""}"
           href="index.html?board=${encodeURIComponent(slug)}&kw=${encodeURIComponent(k.keyword)}"
           title="点击跳转到「${QT.esc(slug)}」榜单并按关键词「${QT.esc(k.keyword)}」筛选"
           style="animation-delay:${i * 40}ms;font-size:${(12 + k.count / kmax * 5).toFixed(1)}px">
           ${QT.esc(k.keyword)} <b>${k.count}</b></a>`).join("") ||
        `<div class="state-block"><p>该榜暂无题材热词</p></div>`;
    } catch { /* 静默 */ }
  }

  // ---- 榜首变迁（时间线）----
  async function loadTimeline() {
    const boards = await QT.fetchJSON("api/boards.json").catch(() => ({ boards: [] }));
    const slug = QT.getParam("board") ||
      (boards.boards || []).find(b => b.date)?.slug;
    if (!slug) return;
    try {
      const s = await QT.fetchJSON(`api/${slug}/market_summary.json`);
      const tl = (s.timeline || []).slice(-10).reverse();
      $("tlList").innerHTML = tl.map(t => `
        <div class="tl-day">
          <span class="tl-date">${t.date.slice(5)}</span>
          <span class="tl-crown">${I.crown(15)}</span>
          <span class="tl-books">${(t.top3 || []).map((b, i) =>
            i === 0 ? `<b>${QT.esc(b.title)}</b>` : QT.esc(b.title)).join(" · ")}</span>
        </div>`).join("") || `<div class="state-block"><p>首日基线，明日起出现变迁</p></div>`;
    } catch { /* 静默 */ }
  }

  // ---- 运行状态 ----
  async function loadStats() {
    try {
      const s = await QT.fetchJSON("api/site-stats.json");
      const rows = [
        [I.check, "成功榜单", `${s.boards_ok} / ${s.boards_total}`],
        [I.book, "在榜书籍", QT.fmtNum(s.total_books) + " 本"],
        [I.layers, "分类覆盖", `${s.total_categories ?? "—"} 个`],
        [I.clock, "抓取耗时", `${s.duration_sec ?? "—"} s`],
        [I.calendar, "最近运行", s.finished_at ? s.finished_at.replace("T", " ") : "—"],
        [I.robot, "分析引擎", s.ai_engine === "AI" ? "大模型 API" : "规则引擎"],
      ];
      $("statList").innerHTML = rows.map(([ic, label, val]) => `
        <div class="heat-row">
          <span class="heat-name" style="width:104px;display:flex;gap:6px;align-items:center;justify-content:flex-end;color:var(--ink-3)">
            ${ic(13)} ${label}</span>
          <span style="flex:1;font-size:13px;font-weight:700;color:var(--ink)">${val}</span>
        </div>`).join("");
      $("topStatus").innerHTML = `
        <span class="status-chip"><span class="pulse-dot"></span><b>${s.boards_ok}</b>/${s.boards_total} 榜</span>
        <span class="status-chip hide-m">${I.calendar(13)} ${s.updated_at?.slice(0, 10) || "—"}</span>`;
    } catch { /* 静默 */ }
  }

  loadBrief(); loadCross(); loadAuthors(); loadHeat();
  loadTimeline(); loadStats();
})();
