/* ============================================================
   看板主逻辑：榜单切换 / 分类 Tab / 书籍卡片 / 黑马雷达 / 作者势力
   ============================================================ */
(() => {
  // ---- 静态文案注入（图标均为 SVG）----
  document.querySelector('[data-nav="index"]').innerHTML = I.grid(16) + " 看板";
  document.querySelector('[data-nav="trend"]').innerHTML = I.compass(16) + " 风向标";
  document.getElementById("sideTitle").innerHTML = I.layers(14) + " 榜单导航";
  document.getElementById("searchIcon").innerHTML = I.search();
  document.getElementById("briefIcon").innerHTML = I.robot(21);
  document.getElementById("headIcon").innerHTML = I.chart(21);
  document.querySelector('[data-sort="rank"]').innerHTML = I.grid(13) + " 榜单序";
  document.querySelector('[data-sort="metric"]').innerHTML = I.coins(13) + " 指标值";
  document.querySelector('[data-sort="rise"]').innerHTML = I.trendUp(13) + " 动能";
  document.getElementById("radarHead").innerHTML =
    I.radar(17) + " 黑马雷达" +
    `<a class="more" href="trend.html">全部 ${I.arrowRight(12)}</a>`;
  document.getElementById("authorHead").innerHTML =
    I.trophy(17) + " 作者势力" +
    `<a class="more" href="trend.html#author">全部 ${I.arrowRight(12)}</a>`;

  const state = {
    boards: [], board: null, data: null,
    cat: null, sort: "rank", keyword: "",
  };

  const $ = (id) => document.getElementById(id);

  // ---- 状态栏 ----
  async function loadStatus() {
    try {
      const s = await QT.fetchJSON("api/site-stats.json");
      $("topStatus").innerHTML = `
        <span class="status-chip"><span class="pulse-dot"></span><b>${s.boards_ok ?? "—"}</b>/${s.boards_total ?? "—"} 榜</span>
        <span class="status-chip hide-m">${I.calendar(13)} ${s.updated_at ? s.updated_at.slice(0, 10) : "—"}</span>
        <span class="status-chip hide-m">${I.book(13)} <b>${QT.fmtNum(s.total_books)}</b> 本在榜</span>`;
    } catch {
      $("topStatus").innerHTML =
        `<span class="status-chip">${I.alert(13)} 数据未构建</span>`;
    }
  }

  // ---- 侧栏榜单列表 ----
  function renderSidebar() {
    const groups = QT.groupBoards(state.boards);
    const labels = { paid: "付费价值盘", traffic: "流量热度盘",
                     newbook: "新书孵化盘", female: "女生频道" };
    const icons = { paid: I.coins, traffic: I.fire, newbook: I.sparkle,
                    female: I.users };
    let html = "";
    for (const [g, list] of Object.entries(groups)) {
      if (!list.length) continue;
      html += `<div class="board-group">
        <div class="board-group-title"><span class="gbar"></span>${labels[g] || g}</div>`;
      for (const b of list) {
        html += `
        <button class="board-btn ${state.board?.slug === b.slug ? "active" : ""}"
                data-slug="${b.slug}">
          ${icons[g] ? icons[g](15) : I.chart(15)}<span>${QT.esc(b.name)}</span>
          <span class="cnt">${b.date ? b.date.slice(5) : "—"}</span>
        </button>`;
      }
      html += `</div>`;
    }
    $("boardList").innerHTML = html;
    $("boardList").querySelectorAll(".board-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        if (state.board?.slug === btn.dataset.slug) return;
        loadBoard(btn.dataset.slug);
      });
    });
  }

  // ---- 加载榜单数据 ----
  async function loadBoard(slug) {
    const board = state.boards.find(b => b.slug === slug);
    if (!board) return;
    state.board = board;
    QT.setParam("board", slug);
    renderSidebar();

    $("boardTitle").textContent = board.name;
    $("boardSub").textContent =
      `${board.group_label} · 核心指标：${board.metric} · 每日抓取各分类 Top 30`;
    $("catTabs").innerHTML = "";
    renderSkeleton();

    try {
      const data = await QT.fetchJSON(`api/${slug}/latest/all.json`);
      state.data = data;
      state.cat = null;
      renderCatTabs(data);
      const first = data.categories?.[0];
      if (first) selectCat(first.name);
    } catch {
      $("bookGrid").innerHTML = `
        <div class="state-block">${I.box()}
        <p>该榜单数据尚未生成，请先运行爬虫与构建脚本</p></div>`;
    }
  }

  function renderSkeleton() {
    $("bookGrid").innerHTML = Array.from({ length: 8 },
      () => `<div class="skeleton-card"></div>`).join("");
  }

  function renderCatTabs(data) {
    const trend = data.analysis?.trends || {};
    const cats = data.categories || [];
    $("catTabs").innerHTML = cats.map(c => {
      const t = trend[c.name] || {};
      const badge = t.new_count ? `<span class="tcnt">+${t.new_count}</span>` : "";
      return `<button class="cat-tab" data-cat="${QT.esc(c.name)}">
        ${QT.esc(c.name)}${badge}</button>`;
    }).join("");
    $("catTabs").querySelectorAll(".cat-tab").forEach(btn =>
      btn.addEventListener("click", () => selectCat(btn.dataset.cat)));
  }

  function selectCat(name) {
    state.cat = name;
    QT.setParam("cat", name);
    $("catTabs").querySelectorAll(".cat-tab").forEach(b =>
      b.classList.toggle("active", b.dataset.cat === name));
    renderBooks();
  }

  // ---- 书籍卡片 ----
  function renderBooks() {
    const cat = state.data?.categories?.find(c => c.name === state.cat);
    if (!cat) return;
    const trend = state.data.analysis?.trends?.[state.cat] || {};
    const prevRank = {};
    (trend.top_movers || []).forEach(m => prevRank[m.title] = m);
    const newTitles = new Set((trend.new_books || []).map(n => n.title));
    const growth = {};
    (trend.metric_growth || []).forEach(g => growth[g.title] = g.growth);

    let books = cat.books.map((b, i) => {
      const m = prevRank[b.title];
      let rankChange = 0;
      if (newTitles.has(b.title)) rankChange = null;
      else if (m) rankChange = m.rankChange ?? 0;
      return { ...b, idx: i, rankChange };
    });

    if (state.keyword) {
      const kw = state.keyword.toLowerCase();
      books = books.filter(b =>
        (b.title || "").toLowerCase().includes(kw) ||
        (b.author || "").includes(state.keyword) ||
        (b.subCategory || "").includes(state.keyword) ||
        (b.category || "").includes(state.keyword) ||
        (b.intro || "").includes(state.keyword));
    }

    if (state.sort === "metric")
      books.sort((a, b) => (b.metric || 0) - (a.metric || 0));
    else if (state.sort === "rise")
      books.sort((a, b) => (b.rankChange ?? -99) - (a.rankChange ?? -99));

    const grid = $("bookGrid");
    if (!books.length) {
      grid.innerHTML = `<div class="state-block">${I.search()}
        <p>没有匹配「${QT.esc(state.keyword)}」的结果</p></div>`;
      return;
    }

    grid.innerHTML = books.map((b, i) => {
      const r = b.rank ?? i + 1;
      const topCls = r === 1 ? "top1" : r === 2 ? "top2" : r === 3 ? "top3" : "";
      let changeHtml = `<span class="rank-change flat">—</span>`;
      if (b.rankChange === null || newTitles.has(b.title))
        changeHtml = `<span class="rank-change new">${I.sparkle(11)} 新上榜</span>`;
      else if (b.rankChange > 0)
        changeHtml = `<span class="rank-change up">${I.arrowUp(11)} ${b.rankChange}</span>`;
      else if (b.rankChange < 0)
        changeHtml = `<span class="rank-change down">${I.arrowDown(11)} ${-b.rankChange}</span>`;

      const metric = (b.metric !== null && b.metric !== undefined)
        ? `<div class="metric-box"><span class="metric-label">${QT.esc(b.metricLabel || state.board?.metric || "")}</span>
           <span class="metric-val" data-countup="${b.metric}">0</span></div>`
        : `<div class="metric-box"><span class="metric-label">指标</span>
           <span class="metric-val plain">—</span></div>`;

      const grow = growth[b.title];
      if (grow) metric; // 增长已隐含在排序中

      return `
      <a class="book-card ${newTitles.has(b.title) ? "is-new" : ""}"
         href="book.html?bid=${b.bid}" style="transition-delay:${Math.min(i * 35, 500)}ms">
        <span class="rank-badge ${topCls}">${r}</span>
        <div class="cover-wrap">
          ${b.cover ? `<img src="${QT.esc(b.cover)}" alt="${QT.esc(b.title)}" loading="lazy"
               onerror="this.parentNode.innerHTML='<div class=cover-fallback>封面加载失败</div>'">`
            : `<div class="cover-fallback">暂无封面</div>`}
        </div>
        <div class="book-info">
          <div class="book-title">${QT.esc(b.title)}</div>
          <div class="book-meta">
            <span class="author">${QT.esc(b.author || "佚名")}</span>
            ${b.subCategory ? `<span class="chip">${QT.esc(b.subCategory)}</span>` : ""}
            ${b.status === "完本" ? `<span class="chip done">完本</span>` : ""}
          </div>
          <div class="book-intro">${QT.esc(b.intro || "暂无简介")}</div>
          <div class="book-foot">
            ${metric}
            ${changeHtml}
          </div>
        </div>
      </a>`;
    }).join("");

    // 弹性入场 + 数字滚动
    requestAnimationFrame(() =>
      requestAnimationFrame(() => {
        grid.querySelectorAll(".book-card").forEach(el => el.classList.add("in"));
        grid.querySelectorAll("[data-countup]").forEach(el =>
          QT.countUp(el, parseInt(el.dataset.countup, 10)));
      }));
  }

  // ---- 黑马雷达（跨榜）----
  async function loadRadar() {
    try {
      const data = await QT.fetchJSON("api/cross-board.json");
      const top = (data.top || []).slice(0, 5);
      $("radarList").innerHTML = top.map((e, i) => `
        <a class="dark-item" href="book.html?bid=${e.bid}">
          <span class="dark-rank ${i < 3 ? "hot" : ""}">${i + 1}</span>
          <span class="dark-info">
            <span class="dark-name">${QT.esc(e.title)}</span>
            <span class="dark-sub">${QT.esc(e.author)} · ${QT.esc(e.subCategory || e.category)}</span>
            <span class="board-tags">${e.boards.slice(0, 3).map(b =>
              `<span class="board-tag">${QT.esc(b.board)}·${b.rank}</span>`).join("")}</span>
          </span>
          <span class="dark-score">${e.momentum}</span>
        </a>`).join("") ||
        `<div class="dark-sub" style="padding:8px">暂无跨榜信号</div>`;
    } catch {
      $("radarList").innerHTML =
        `<div class="dark-sub" style="padding:8px">跨榜数据未构建</div>`;
    }
  }

  // ---- 作者势力 ----
  async function loadAuthors() {
    try {
      const slug = state.board?.slug || state.boards[0]?.slug;
      if (!slug) return;
      const s = await QT.fetchJSON(`api/${slug}/market_summary.json`);
      const top = (s.author_power || []).slice(0, 5);
      $("authorList").innerHTML = top.map((a, i) => `
        <div class="author-item">
          <span class="dark-rank ${i < 3 ? "hot" : ""}">${i + 1}</span>
          <span class="dark-info">
            <span class="dark-name">${QT.esc(a.author)}</span>
            <span class="dark-sub">${a.books} 本在榜 · 最佳第 ${a.bestRank} 名</span>
          </span>
          <span class="dark-score">${a.top10}<span style="font-size:9px;color:var(--ink-3)">次十强</span></span>
        </div>`).join("") ||
        `<div class="dark-sub" style="padding:8px">暂无数据</div>`;
    } catch {
      $("authorList").innerHTML =
        `<div class="dark-sub" style="padding:8px">暂无数据</div>`;
    }
  }

  // ---- AI 日报 ----
  async function loadBrief() {
    try {
      const b = await QT.fetchJSON("api/market-brief.json");
      $("briefLabel").innerHTML =
        `今日起点风向日报 ${b.engine === "AI" ? '<span class="engine-tag">AI 生成</span>' : '<span class="engine-tag">规则引擎</span>'}`;
      $("briefText").textContent = b.brief || "暂无日报。";
    } catch {
      $("briefText").textContent = "日报未生成：请先运行构建脚本或配置 AI Secrets。";
    }
  }

  // ---- 工具栏事件 ----
  $("filterChipIcon").innerHTML = I.tag(13);
  function syncFilterChip() {
    const chip = $("filterChip");
    if (!chip) return;
    if (state.keyword) {
      $("filterChipText").textContent = state.keyword;
      chip.hidden = false;
    } else { chip.hidden = true; }
  }
  $("filterChip").addEventListener("click", () => {
    state.keyword = "";
    $("searchInput").value = "";
    syncFilterChip();
    QT.setParam("kw", null);
    renderBooks();
  });
  let searchTimer;
  $("searchInput").addEventListener("input", (e) => {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(() => {
      state.keyword = e.target.value.trim();
      QT.setParam("kw", state.keyword || null);
      syncFilterChip();
      renderBooks();
    }, 180);
  });
  $("sortSeg").querySelectorAll("button").forEach(btn =>
    btn.addEventListener("click", () => {
      state.sort = btn.dataset.sort;
      $("sortSeg").querySelectorAll("button").forEach(b =>
        b.classList.toggle("on", b === btn));
      renderBooks();
    }));

  // ---- 启动 ----
  (async function init() {
    loadBrief();
    loadRadar();
    loadStatus();
    // 从题材风向等外部链接带入的关键词筛选（?kw=穿越）
    const urlKw = QT.getParam("kw");
    if (urlKw) {
      state.keyword = urlKw;
      const input = $("searchInput");
      if (input) input.value = urlKw;
    }
    syncFilterChip();
    try {
      const idx = await QT.fetchJSON("api/boards.json");
      state.boards = idx.boards || [];
      renderSidebar();
      const fromURL = QT.getParam("board");
      const fallback = state.boards.find(b => b.date) || state.boards[0];
      loadBoard(fromURL && state.boards.some(b => b.slug === fromURL)
        ? fromURL : fallback.slug);
      loadAuthors();
    } catch {
      $("boardTitle").textContent = "数据尚未初始化";
      $("boardGrid").innerHTML = `<div class="state-block">${I.alert()}
        <p>api/boards.json 不存在 —— 请先运行 python scrape_qidian.py --build</p></div>`;
    }
  })();
})();
