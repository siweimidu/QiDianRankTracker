"""
起点字体反爬动态解码。

起点把榜单数字（月票/推荐票/收藏…）渲染成自定义 woff 字体的
私有区码位（PUA），且每个页面随机换字体文件、随机映射。

破解思路（零硬编码，永久自适应）：
  1. 从 SSR HTML 的 @font-face 提取该页使用的 woff URL
  2. fontTools 解析 cmap：PUA 码位 → 字形名
  3. 字形名本身就是明文：zero/one/.../nine/period
  4. 结果按 URL 缓存，同页 20 本书共享一次解析
"""
import io
from functools import lru_cache

import requests
from fontTools.ttLib import TTFont

_GLYPH_NAMES = {
    "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
    "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9",
    "period": ".", "comma": ",", "colon": ":",
}


@lru_cache(maxsize=64)
def _build_map(font_url: str) -> dict:
    """下载 woff 并返回 {PUA字符: 数字字符} 映射。"""
    r = requests.get(font_url, timeout=20,
                     headers={"User-Agent": "Mozilla/5.0", "Referer":
                              "https://www.qidian.com/"})
    r.raise_for_status()
    font = TTFont(io.BytesIO(r.content), fontNumber=0, lazy=True)
    cmap = font.getBestCmap()
    mapping = {}
    for cp, glyph in cmap.items():
        ch = _GLYPH_NAMES.get(glyph)
        if ch:
            mapping[chr(cp)] = ch
    return mapping


def decode(text: str, font_url: str) -> str:
    """把 PUA 混淆文本解码为明文数字；无字体时原样返回。"""
    if not text or not font_url:
        return text
    try:
        mapping = _build_map(font_url)
    except Exception as e:  # noqa: BLE001
        print(f"    [FONT] 字体解析失败（{str(e)[:80]}），保留原值")
        return text
    if not any(c in mapping for c in text):
        return text  # 本就是明文
    return "".join(mapping.get(c, c) for c in text)


def to_int(text: str) -> int | None:
    """'10849' / '1.2万' → int（万单位换算）；解析失败返回 None。"""
    if not text:
        return None
    t = text.strip().replace(",", "")
    try:
        if t.endswith("万"):
            return int(float(t[:-1]) * 10000)
        if t.endswith("亿"):
            return int(float(t[:-1]) * 100000000)
        return int(float(t))
    except ValueError:
        return None
