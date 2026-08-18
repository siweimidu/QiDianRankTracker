/* ============================================================
   书籍档案页：bid → 多榜出现轨迹（book-index.json 驱动）
   ============================================================ */
(() => {
  document.querySelector('[data-nav="index"]').innerHTML = I.grid(16) + " 看板";
  document.querySelector('[data-nav="trend"]').innerHTML = I.compass(16) + " 风向标";
  document.getElementById("headIcon").innerHTML = I.book(21);

  const $ = (id) => document.getElementById(id);
  const bid = QT.getParam("bid");

  if (!bid) {
    $("hero").innerHTML = `<div class="state-block" style="grid-column:1/-1">
      ${I.alert()}<p>缺少 ?bid= 参数，请从看板或黑马雷达进入</p></div>`;
    return;
  }

  (async () => {
    try {
      const idx = await QT.fetchJSON("api/book-index.json");
      const b = idx.books[bid];
      if (!b) throw new Error("not found");
      document.title = `${b.title} · 书籍档案 | 起点·风向标`;

      $("hero").innerHTML = `
        <div class="hero-cover">
          ${b.cover ? `<img src="${QT.esc(b.cover)}" alt="${QT.esc(b.title)}"
            onerror="this.parentNode.innerHTML='<div class=cover-fallback style=position:absolute;inset:0;display:grid;place-items:center;color:#6b7691;font-size:12px>封面加载失败</div>'">`
            : `<div class="cover-fallback">暂无封面</div>`}
        </div>
        <div class="hero-body">
          <div class="hero-author">
            ${I.pen(15)} ${QT.esc(b.author || "佚名")}
            <a href="${QT.esc(b.bookUrl)}" target="_blank" rel="noopener"
               class="chip" style="text-decoration:none;display:inline-flex;align-items:center;gap:4px">
               ${I.external(11)} 起点书页</a>
          </div>
          <div class="hero-title">${QT.esc(b.title)}
            <span class="rank-change ${b.boardCount >= 4 ? "up" : "flat"}"
              style="font-size:13px;padding:5px 12px">
              ${I.layers(13)} ${b.boardCount} 榜在列</span>
          </div>
          <div class="hero-chips">
            ${b.category ? `<span class="chip">${QT.esc(b.category)}</span>` : ""}
            ${b.subCategory ? `<span class="chip gold">${QT.esc(b.subCategory)}</span>` : ""}
            ${b.status ? `<span class="chip ${b.status === "完本" ? "done" : ""}">${QT.esc(b.status)}</span>` : ""}
          </div>
          <div class="hero-intro">${QT.esc(b.intro || "暂无简介")}</div>
        </div>`;

      const aps = b.appearances || [];
      $("apSub").textContent = `出现在 ${new Set(aps.map(a => a.slug)).size} 个榜单 / ${aps.length} 个分类`;
      $("appearGrid").innerHTML = aps.map((a, i) => `
        <a class="appear-card" href="index.html?board=${a.slug}"
           style="transition-delay:${Math.min(i * 45, 500)}ms">
          <div class="appear-top">
            <span class="appear-board">${QT.esc(a.board)}</span>
            <span class="appear-rank">#${a.rank}</span>
          </div>
          <div class="appear-metric">${a.category} 分类 ·
            ${a.metric !== null && a.metric !== undefined
              ? `${QT.esc(a.metricLabel)} <b>${QT.fmtNum(a.metric)}</b>` : "无量值指标"}</div>
        </a>`).join("");
      requestAnimationFrame(() => requestAnimationFrame(() =>
        document.querySelectorAll(".appear-card").forEach(el =>
          el.classList.add("in"))));

      $("topStatus").innerHTML =
        `<span class="status-chip">${I.book(13)} ${QT.esc(b.title)}</span>`;
    } catch {
      $("hero").innerHTML = `<div class="state-block" style="grid-column:1/-1">
        ${I.box()}<p>未找到 bid=${QT.esc(bid)} 的书籍（可能尚未上榜）</p></div>`;
    }
  })();
})();
