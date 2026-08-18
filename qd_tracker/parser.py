"""
SSR HTML 解析器 —— 分类发现 + 书籍卡片抽取。

起点榜单页为服务端渲染，requests 拿到的 HTML 已包含全部数据：
  * 分类目录：<a data-chanid="21">玄幻</a>
  * 书卡：<li data-rid="1"> … 标题/作者/大小分类/状态/简介/更新/封面/指标
  * 指标数字：@font-face 内联 woff + PUA 字符（交由 font.py 解码）
"""
import html as html_lib
import re

from . import font as fontdec

# ---- 分类发现：data-chanid 导航（保持页面顺序，去重） ----
_CHANID_RE = re.compile(
    r'<a\s+data-chanid="(-?\d+)"[^>]*>([^<]{1,12})</a>')

# ---- 书卡切块 ----
_LI_RE = re.compile(r'<li data-rid="(\d+)">(.*?)</li>', re.S)

_BID_RE = re.compile(r'href="//www\.(?:qidian|qdmm)\.com/book/(\d+)/"')
_TITLE_RE = re.compile(r'<h2><a[^>]*>([^<]+)</a></h2>')
_AUTHOR_RE = re.compile(r'<a class="name" title="([^"]*)"')
# 作者|大类·小类|状态（· 在原始 HTML 中是 &#183; 实体）
_META_RE = re.compile(
    r'<a class="name"[^>]*>[^<]*</a><em>\|</em>'
    r'<a href="[^"]*"[^>]*>([^<]+)</a>'
    r'(?:<i>[^<]*</i>)?'
    r'(?:<a class="go-sub-type"[^>]*>([^<]+)</a>)?'
    r'(?:<i>[^<]*</i>|<em>[^<]*</em>)*'
    r'<span>([^<]+)</span>')
_INTRO_RE = re.compile(r'<p class="intro">\s*(.*?)\s*</p>', re.S)
_UPDATE_RE = re.compile(
    r'<p class="update"><a[^>]*>(?:最新更新\s*)?([^<]*)</a>'
    r'(?:<em>[^<]*</em>)?<span>([^<]*)</span>')
_COVER_RE = re.compile(r'<img src="(//bookcover[^"]+)"')

# ---- 指标区：<style>@font-face{...woff...}</style><span class="X">PUA</span></span>月票</p>
_FONT_FACE_RE = re.compile(r"url\('(https://[^']+?\.woff)'")
_METRIC_RE = re.compile(
    r'<span class="[^"]+">([^<]+)</span>\s*(?:</span>)?\s*'
    r'([^<]{0,10}?)\s*</p>')

_TAG_RE = re.compile(r"<[^>]+>")


def discover_categories(page_html: str) -> list:
    """从榜单页提取分类目录：[{chanid, name}]，保持页面顺序。"""
    seen, cats = set(), []
    for chanid, name in _CHANID_RE.findall(page_html):
        name = html_lib.unescape(name).strip()
        if not name or name in ("排行",):
            continue
        key = (chanid, name)
        if key in seen:
            continue
        seen.add(key)
        cats.append({"chanid": chanid,
                     "name": "全部" if chanid == "-1" else name})
    return cats


def _clean(text: str) -> str:
    return _TAG_RE.sub("", html_lib.unescape(text or "")).strip()


def parse_books(page_html: str) -> list:
    """解析一页（20 本）书卡。指标解码延后到 scrape 层（需 font url 上下文）。"""
    books = []
    for rank, chunk in _LI_RE.findall(page_html):
        bid_m = _BID_RE.search(chunk)
        title_m = _TITLE_RE.search(chunk)
        if not bid_m or not title_m:
            continue
        author_m = _AUTHOR_RE.search(chunk)
        meta_m = _META_RE.search(chunk)
        if meta_m:
            category = _clean(meta_m.group(1))
            sub_category = _clean(meta_m.group(2) or "")
            status = _clean(meta_m.group(3) or "")
        else:
            category = sub_category = status = ""
        intro_m = _INTRO_RE.search(chunk)
        upd_m = _UPDATE_RE.search(chunk)
        cover_m = _COVER_RE.search(chunk)
        # 指标：本块内的字体 + PUA 文本 + 单位
        font_m = _FONT_FACE_RE.search(chunk)
        metric_raw, metric_label = "", ""
        metric_m = _METRIC_RE.search(chunk)
        if metric_m and font_m:
            metric_raw = html_lib.unescape(metric_m.group(1)).strip()
            metric_label = _clean(metric_m.group(2))
        books.append({
            "rank": int(rank),
            "bid": bid_m.group(1),
            "title": _clean(title_m.group(1)),
            "author": _clean(author_m.group(1)) if author_m else "",
            "category": category,
            "subCategory": sub_category,
            "status": status,
            "intro": _clean(intro_m.group(1))[:120] if intro_m else "",
            "latestChapter": _clean(upd_m.group(1))[:60] if upd_m else "",
            "updateTime": _clean(upd_m.group(2)) if upd_m else "",
            "cover": ("https:" + cover_m.group(1)) if cover_m else "",
            "bookUrl": f"https://www.qidian.com/book/{bid_m.group(1)}/",
            "_fontUrl": font_m.group(1) if (font_m and metric_raw) else "",
            "_metricRaw": metric_raw,
            "metricLabel": metric_label,
        })
    return books


def finalize_metrics(books: list) -> list:
    """用页面字体解码指标并转为数值，清理内部字段。"""
    out = []
    for b in books:
        font_url = b.pop("_fontUrl", "")
        raw = b.pop("_metricRaw", "")
        decoded = fontdec.decode(raw, font_url) if raw else ""
        b["metric"] = fontdec.to_int(decoded) if decoded else None
        b["metricText"] = decoded if decoded else ""
        out.append(b)
    return out
