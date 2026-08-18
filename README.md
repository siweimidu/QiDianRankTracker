# 起点·风向标 · QiDian Rank Tracker

[![Deploy](https://img.shields.io/badge/deploy-GitHub%20Pages-4cc3e8)](https://github.com/siweimidu/QiDianRankTracker)
[![Actions](https://img.shields.io/badge/Automation-GitHub%20Actions-e6584b)](https://github.com/siweimidu/QiDianRankTracker/actions)

> 追踪**起点中文网全部 21 个排行榜**（男频 14 榜：月票 / 畅销 / 畅读指数 / 追读 / 收藏 / 推荐 / 留存 / 更新 / VIP 收藏 / 书友 / 四大新书榜；女生频道 7 榜：月票 / 畅销 / 推荐 / 收藏 / 书友 / 阅读指数 / 签约新书），每日自动抓取各分类 **Top 30**，结合 AI 生成趋势分析，部署为精美的在线看板。

---

## ✨ 功能概览

| 功能 | 说明 |
|------|------|
| 🕷️ 混合高速抓取 | Playwright 隐身浏览器仅需通过一次腾讯云 WAF 握手，之后纯 HTTP 会话批量抓取 —— 男频单榜 16 分类 × 30 本仅 ~35 秒，比逐页浏览器方案快 **5~8 倍** |
| 🔓 字体反爬动态破解 | 起点把月票/推荐票等数字渲染成随机映射的自定义字体，本项目用 fontTools 实时解析 woff cmap（字形名即明文数字），**零硬编码映射表，字体怎么换都能解** |
| 🧭 分类自动发现 | 各榜单分类（玄幻/仙侠/都市…女生频道子类）从榜单页 `data-chanid` 导航自动发现，起点改版零维护 |
| 📊 趋势对比 | 自动对比相邻两日：新上榜 / 掉榜 / 排名变化 / 指标真实增长量（数字已解码，非模糊文本） |
| 🚀 动能分引擎 | 排名变化 + 指标环比增长对数压缩合成为「动能分」，跨书可比、跨榜可比 |
| 🤖 AI 风向分析 | OpenAI 兼容 API 生成每分类速评 + 全站日报；未配置自动规则兜底，纯 requests 实现零额外依赖 |
| 🕵️ 黑马雷达 | 跨 21 榜聚合：一本书同时出现在多榜且排名上升 → 市场合力信号 |
| 👑 作者势力榜 | 同一作者多书上榜的统治力排名（在榜数 / 十强次数 / 最佳名次） |
| 📖 书籍档案页 | 任意书籍在全部榜单中的出现轨迹（排名 + 指标），`api/book-index.json` 驱动 |
| 🖥️ 液态玻璃看板 | 深空商务风 · 液态玻璃 · 弹性动画（spring 缓动）· 全 SVG 图标 · 骨架屏 · 数字滚动 |
| 🔌 静态数据接口 | `api/` 目录 JSON 接口，GitHub Pages 直接可访问，可二次开发 |
| ⚡ 全自动化 | GitHub Actions + GitHub Pages，零服务器、零运维、零成本 |

---

## 🚀 食用指南

### 前置条件

- 一个 GitHub 账号
- （可选）一个 OpenAI 兼容 API 密钥（Moonshot / DeepSeek / GLM / GPT 均可）

### 第一步：Fork 仓库

点击本页右上角 **Fork**，将项目 Fork 到你的账号下。

### 第二步：启用 GitHub Pages

1. 进入你 Fork 后的仓库 → **Settings** → **Pages**
2. **Source** 选择 **Deploy from a branch**，Branch 选 `main`、目录 `/ (root)` → **Save**

> 也可以不做这一步：每日 Workflow 会自动通过 Actions 部署 Pages（本仓库采用内联部署，无需手动配置也能上线）。手动配置 Branch 源可作为兜底。

### 第三步：配置 AI Secrets（可选）

仓库 → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**：

| Secret | 说明 | 示例 |
|---|---|---|
| `API_BASE_URL` | OpenAI 兼容 API 地址 | `https://api.moonshot.cn/v1` |
| `API_KEY` | API 密钥 | `sk-xxxx` |
| `API_MODEL` | 模型名 | `moonshot-v1-8k` |

> 💡 不配置也完全可用：系统自动切换到基于规则的中文速评，功能不受影响。

### 第四步：手动触发首次运行

1. 仓库 → **Actions** → 左侧 **Daily QiDian Rank Scraper**
2. 右上角 **Run workflow** → **Run workflow**
3. 等待运行完成（全量 21 榜约 8~15 分钟）

运行成功后打开：`https://<你的用户名>.github.io/QiDianRankTracker/`

### 第五步：坐等每日更新

Workflow 每天 **UTC 20:17（北京时间次日 04:17）** 自动运行：抓取 → 趋势分析 → AI 速评 → 提交数据 → 部署 Pages。看板顶部的状态芯片会显示当前数据日期。

**Force Rebuild Dashboard** 工作流：不重新抓取，仅重建分析/速评/API 并重新部署 —— 配好 AI Secrets 后立即重跑分析，或勾选 `force_ai` 忽略当日缓存强制重新生成 AI 文案。

---

## 🔌 静态数据接口

| 类型 | 路径 | 说明 |
|---|---|---|
| 榜单索引 | `api/boards.json` | 全部榜单 slug / 分组 / 最新日期 |
| 类型索引 | `api/<slug>/latest.json` | 该榜所有分类及对应 URL |
| 全量数据 | `api/<slug>/latest/all.json` | 该榜全部分类 + 趋势分析 + 书籍 |
| 单分类数据 | `api/<slug>/latest/<分类>.json` | 如 `api/yuepiao/latest/玄幻.json` |
| 跨榜影响力 | `api/cross-board.json` | 多榜同时上榜的黑马雷达 Top30 |
| 书籍索引 | `api/book-index.json` | bid → 多榜出现轨迹 |
| 风向日报 | `api/market-brief.json` | AI / 规则生成的全站日报 |
| 运行统计 | `api/site-stats.json` | 抓取成功率 / 书籍量 / 引擎 |

示例：

```bash
curl https://<用户名>.github.io/QiDianRankTracker/api/boards.json
curl https://<用户名>.github.io/QiDianRankTracker/api/yuepiao/latest/仙侠.json
```

榜单 slug 一览：`yuepiao`（月票）、`hotsales`（畅销）、`retention`（留存）、`readindex`（阅读指数）、`newfans`（书友）、`recom`（推荐）、`followreading`（追读）、`collect`（收藏）、`vipup`（更新）、`vipcollect`（VIP收藏）、`signnewbook` / `pubnewbook` / `newsign` / `newauthor`（四大新书榜）、`female-yuepiao`（女生月票）、`female-hotsales`（女生畅销）、`female-recom`（女生推荐）、`female-collect`（女生收藏）、`female-newfans`（女生书友）、`female-readindex`（女生阅读指数）、`female-newsign`（女生签约新书）。

---

## 🔧 本地开发

```bash
# 1. 克隆
git clone https://github.com/siweimidu/QiDianRankTracker.git
cd QiDianRankTracker

# 2. 安装依赖（建议虚拟环境）
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium

# 3. 首次全量抓取（16 榜 × 各分类 Top 30，约 10 分钟）
python scrape_qidian.py

# 4. 构建看板数据 + AI/规则分析
python scripts/build_latest.py
# 带 AI：
export API_BASE_URL="https://api.moonshot.cn/v1"
export API_KEY="sk-xxx" API_MODEL="moonshot-v1-8k"
python scripts/build_latest.py

# 5. 本地预览
python -m http.server 8000
# 打开 http://localhost:8000
```

常用参数：

```bash
python scrape_qidian.py --only yuepiao recom   # 只抓部分榜单
python scrape_qidian.py --top 50               # 每分类 Top 50
python scrape_qidian.py --sleep 0.5            # 调小分类间隔（更快）
python scrape_qidian.py --build                # 抓完顺带构建
```

---

## 📁 项目结构

```
QiDianRankTracker/
├── .github/workflows/
│   ├── scrape.yml                 # 每日抓取 + 构建 + 提交 + 部署 Pages
│   └── force_update.yml           # 手动重建分析 / 重新部署
├── qd_tracker/                    # 核心包
│   ├── browser.py                 # Playwright 隐身握手过腾讯云 WAF
│   ├── fetcher.py                 # WAF Cookie 复用的高速 HTTP 会话（自愈重握手）
│   ├── font.py                    # 字体反爬动态解码（fontTools cmap）
│   ├── parser.py                  # SSR HTML 解析（分类发现 + 书卡抽取）
│   ├── config.py                  # 21 榜单注册表 + 题材关键词（单一事实源）
│   ├── scrape.py                  # 抓取编排（断点续跑 + 增量快照 + 限速）
│   ├── analyze.py                 # 趋势分析（动能分 / 黑马 / 作者势力 / 赛道热度）
│   ├── ai.py                      # OpenAI 兼容速评（纯 requests）+ 规则兜底
│   └── build.py                   # 数据聚合 + 静态 API 构建
├── scripts/build_latest.py        # 构建 CLI 入口
├── scrape_qidian.py               # 抓取 CLI 入口
├── css/style.css                  # 液态玻璃主题（深空商务 + spring 动效）
├── js/                            # icons(SVG库) / boards(工具) / app / trend / book
├── index.html                     # 看板：榜单×分类×书籍卡片 + 黑马雷达 + 作者势力
├── trend.html                     # 风向标：跨榜影响力 / 分类热度 / 题材云 / 榜首变迁
├── book.html                      # 书籍档案：多榜出现轨迹
├── data/                          # 每日快照 + 趋势 + AI 缓存（按榜分目录）
├── api/                           # 静态 JSON 接口（Pages 直出）
└── requirements.txt
```

---

## ⚙️ 工作流程

```
 GitHub Actions（每日 04:17 北京时间）
 ┌────────────────┐   ┌────────────────┐   ┌───────────────┐
 │ Playwright 握手 │ → │ 纯 HTTP 全量抓取 │ → │ 趋势分析 + AI  │
 │ 通过腾讯云 WAF   │   │ 21榜×分类×Top30 │   │ 速评/黑马/势力 │
 └────────────────┘   └────────────────┘   └───────┬───────┘
                                                   ▼
                                  git commit (data/ api/) → Pages 部署
                                            在线看板 🌐
```

---

## 🛡️ 反爬对抗说明（本项目核心工程点）

1. **腾讯云 WAF**：起点 www 站对普通请求返回 JS 挑战、对自动化浏览器返回 TCaptcha 验证码。本项目用一组克制的浏览器指纹补丁（隐藏 `navigator.webdriver` 等）+ 关闭自动化特征启动参数通过验证，仅做一次握手获取 Cookie。
2. **字体数字混淆**：榜单指标数字使用每次随机生成的私有字体渲染。项目直接下载页面内联 woff，用 fontTools 读取 cmap —— 字形名本身就是 `zero/one/.../nine`，天然自适应任何字体更换。
3. **友好抓取**：全局限速 0.55s + 随机抖动，指数退避重试，断点续跑；单日一次全量运行，不做高频请求。
4. 本项目仅抓取公开榜单聚合数据用于趋势研究，不抓取正文内容，请合理使用。

---

## 📝 常见问题

<details>
<summary><b>Workflow 里 WAF 握手失败怎么办？</b></summary>

GitHub Actions 的数据中心 IP 偶尔会被 WAF 重点关照。Workflow 内置 3 次指数退避重试；若仍失败，在 Actions 页面重新 Run workflow 即可（换一台 runner IP 通常即可恢复）。

</details>

<details>
<summary><b>为什么畅销榜/更新榜没有数字指标？</b></summary>

起点部分榜单页面本身不展示数值（如畅销榜），卡片会显示「—」，属正常现象；趋势对比仍基于排名变化进行。

</details>

<details>
<summary><b>想增减榜单？</b></summary>

编辑 `qd_tracker/config.py` 的 `BOARDS`，把对应榜单 `enabled` 设为 `False`，或按 path 规律新增。分类无需配置，全部自动发现。

</details>

<details>
<summary><b>封面图加载失败？</b></summary>

起点封面 CDN（bookcover.yuewen.com）偶尔对高频请求限流，卡片会自动降级为占位样式，不影响其他功能。

</details>

---

## 📜 License

MIT —— 数据归起点中文网所有，本项目仅做聚合分析与展示。

---

<p align="center"><sub>Made with ☕ and 🤖 · 混合抓取 · 字体反爬动态破解 · 全自动运行</sub></p>
