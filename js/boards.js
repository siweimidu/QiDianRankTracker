/* ============================================================
   共享工具：数据获取 / 榜单分组 / 数字格式化 / URL 同步
   ============================================================ */
const QT = (() => {

  const fetchJSON = async (url) => {
    const r = await fetch(url, { cache: "no-cache" });
    if (!r.ok) throw new Error(`${url} → HTTP ${r.status}`);
    return r.json();
  };

  // "37430" → "3.7万"；812 → "812"
  const fmtNum = (n) => {
    if (n === null || n === undefined || isNaN(n)) return "—";
    if (Math.abs(n) >= 100000000) return (n / 100000000).toFixed(2) + "亿";
    if (Math.abs(n) >= 10000) return (n / 10000).toFixed(1).replace(/\.0$/, "") + "万";
    return String(n);
  };

  const fmtDelta = (n) => {
    if (n === null || n === undefined) return "";
    if (Math.abs(n) >= 10000) return (n > 0 ? "+" : "") + (n / 10000).toFixed(1) + "万";
    return (n > 0 ? "+" : "") + n;
  };

  const GROUP_ORDER = ["paid", "traffic", "newbook", "female"];

  const groupBoards = (boards) => {
    const map = {};
    for (const g of GROUP_ORDER) map[g] = [];
    for (const b of boards) (map[b.group] || (map[b.group] = [])).push(b);
    return map;
  };

  // ?board=slug 与 ?cat= 同步
  const getParam = (k) => new URLSearchParams(location.search).get(k);
  const setParam = (k, v) => {
    const u = new URL(location);
    if (v === null || v === undefined) u.searchParams.delete(k);
    else u.searchParams.set(k, v);
    history.replaceState(null, "", u);
  };

  // 数字滚动动画
  const countUp = (el, target, dur = 900) => {
    if (!el || !target || target < 10) { if (el) el.textContent = fmtNum(target); return; }
    const t0 = performance.now();
    const step = (t) => {
      const p = Math.min((t - t0) / dur, 1);
      const eased = 1 - Math.pow(1 - p, 3);
      el.textContent = fmtNum(Math.round(target * eased));
      if (p < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  };

  const esc = (s) => String(s ?? "").replace(/[&<>"']/g,
    (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

  // 相对天数
  const daysAgo = (dateStr) => {
    const d = new Date(dateStr + "T00:00:00");
    const diff = Math.floor((Date.now() - d.getTime()) / 86400000);
    if (diff <= 0) return "今天";
    if (diff === 1) return "昨天";
    return `${diff} 天前`;
  };

  return { fetchJSON, fmtNum, fmtDelta, groupBoards, getParam, setParam,
           countUp, esc, daysAgo };
})();
