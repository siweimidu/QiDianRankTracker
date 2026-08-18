/* ============================================================
   SVG 图标库 —— 全站唯一图标来源（严禁颜文字/emoji 充当图标）
   用法：I.iconName(size, extraClass) 返回 SVG 字符串
   ============================================================ */
const I = (() => {
  const wrap = (paths, vb = "0 0 24 24") => (size = 16, cls = "") =>
    `<svg class="${cls}" width="${size}" height="${size}" viewBox="${vb}" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${paths}</svg>`;

  return {
    // 品牌 / 导航
    crown: wrap('<path d="M3 8l4.5 4L12 5l4.5 7L21 8l-1.5 11h-15L3 8z"/>'),
    grid: wrap('<rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/>'),
    compass: wrap('<circle cx="12" cy="12" r="9"/><path d="M15.5 8.5l-2 5-5 2 2-5 5-2z"/>'),
    layers: wrap('<path d="M12 2l9 5-9 5-9-5 9-5z"/><path d="M3 12l9 5 9-5"/><path d="M3 17l9 5 9-5"/>'),
    book: wrap('<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20V4H6.5A2.5 2.5 0 0 0 4 6.5v13z"/><path d="M4 19.5A2.5 2.5 0 0 0 6.5 22H20v-5"/>'),
    calendar: wrap('<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M8 3v4M16 3v4M3 10h18"/>'),
    clock: wrap('<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3.5 2"/>'),
    check: wrap('<path d="M4 12l5 5L20 6"/>'),

    // 数据 / 趋势
    trendUp: wrap('<path d="M3 17l6-6 4 4 8-8"/><path d="M14 7h7v7"/>'),
    trendDown: wrap('<path d="M3 7l6 6 4-4 8 8"/><path d="M14 17h7v-7"/>'),
    chart: wrap('<path d="M3 3v18h18"/><rect x="7" y="12" width="3" height="6" rx="0.8"/><rect x="12" y="8" width="3" height="10" rx="0.8"/><rect x="17" y="5" width="3" height="13" rx="0.8"/>'),
    fire: wrap('<path d="M12 22c4.4 0 7.5-2.9 7.5-7 0-3-1.8-5.2-3.3-6.8C14.7 6.6 14 5 14 3c-3 2-4.2 4.6-4.2 6.5-1.2-.6-2-1.8-2.3-3C5.9 8.5 4.5 11 4.5 13.5 4.5 19.1 7.6 22 12 22z"/>'),
    radar: wrap('<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1" fill="currentColor"/><path d="M12 12L18 5"/>'),
    sparkle: wrap('<path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8L12 3z"/><path d="M19 15l.9 2.1L22 18l-2.1.9L19 21l-.9-2.1L16 18l2.1-.9L19 15z"/>'),
    robot: wrap('<rect x="4" y="8" width="16" height="11" rx="2.5"/><path d="M12 8V4M9 4h6"/><circle cx="9" cy="13" r="1" fill="currentColor"/><circle cx="15" cy="13" r="1" fill="currentColor"/><path d="M9.5 16.5h5"/>'),
    trophy: wrap('<path d="M8 21h8M12 17v4"/><path d="M7 4h10v5a5 5 0 0 1-10 0V4z"/><path d="M7 6H4a3 3 0 0 0 3 5M17 6h3a3 3 0 0 1-3 5"/>'),
    pen: wrap('<path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/>'),
    search: wrap('<circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/>'),
    arrowUp: wrap('<path d="M12 19V5M5 12l7-7 7 7"/>'),
    arrowDown: wrap('<path d="M12 5v14M5 12l7 7 7-7"/>'),
    arrowRight: wrap('<path d="M5 12h14M13 6l6 6-6 6"/>'),
    external: wrap('<path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><path d="M15 3h6v6M10 14L21 3"/>'),
    tag: wrap('<path d="M20.6 13.4L12 22l-9-9 8.6-8.6a2 2 0 0 1 1.4-.6H19a2 2 0 0 1 2 2v6.2a2 2 0 0 1-.4 1.8z"/><circle cx="16.5" cy="7.5" r="1.2" fill="currentColor"/>'),
    coins: wrap('<circle cx="9" cy="9" r="5.5"/><path d="M14.2 7.3A5.5 5.5 0 1 1 7.3 14.2"/><path d="M11 13.5a5.5 5.5 0 1 1-6.9 6.9"/>'),
    eye: wrap('<path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7z"/><circle cx="12" cy="12" r="3"/>'),
    users: wrap('<circle cx="9" cy="8" r="3.5"/><path d="M2.5 21c0-3.6 2.9-6 6.5-6s6.5 2.4 6.5 6"/><path d="M16 4.6a3.5 3.5 0 0 1 0 6.8M17.5 15.3c2.4.7 4 2.6 4 5.7"/>'),
    refresh: wrap('<path d="M21 12a9 9 0 1 1-2.6-6.4"/><path d="M21 3v6h-6"/>'),
    box: wrap('<path d="M21 8l-9-5-9 5v8l9 5 9-5V8z"/><path d="M3 8l9 5 9-5M12 13v9"/>'),
    alert: wrap('<path d="M12 3l10 17H2L12 3z"/><path d="M12 10v4M12 17.5v.5"/>'),
  };
})();

if (typeof module !== "undefined") module.exports = I;
