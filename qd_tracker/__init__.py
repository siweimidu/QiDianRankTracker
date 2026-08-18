"""QiDianRankTracker —— 起点中文网排行榜追踪核心包。

架构（混合抓取，本项目的核心创新）：
  browser.py   Playwright 隐身浏览器，仅用于通过腾讯云 WAF 握手拿 Cookie
  fetcher.py   纯 HTTP 会话复用 WAF Cookie 高速抓取（快 5~8 倍），挑战自动重握手
  font.py      动态破解起点字体反爬（fontTools 解析 woff cmap，零硬编码表）
  parser.py    SSR HTML → 分类目录 / 书籍卡片
  config.py    榜单注册表（单一事实源）
  scrape.py    抓取编排（分类自动发现 + 断点续跑 + 增量快照）
  analyze.py   趋势分析（diff / 动能分 / 黑马 / 作者势力 / 赛道热度）
  ai.py        OpenAI 兼容趋势速评（纯 requests 实现，无额外依赖）+ 规则兜底
  build.py     构建 latest 数据与静态 API
"""

__version__ = "1.0.0"
