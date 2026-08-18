"""
趋势分析 —— 单榜 diff / 动能分 / 黑马 / 作者势力 / 赛道热度 + 跨榜聚合。

相对原版（番茄追踪器）的增强：
  * 指标是真数值（字体反爬已破），可计算真实增长量与环比
  * 动能分（momentum）：排名变化 + 指标增长归一合成，单本书跨榜可比
  * 作者势力榜：同一作者多书上榜的统治力排名
  * 跨榜黑马雷达：多榜同时上升的书（市场合力信号）
"""
import glob
import json
import os
from datetime import datetime

from .config import (BOARDS, FEMALE_KEYWORDS, GENERAL_KEYWORDS,
                     MALE_KEYWORDS, enabled_boards)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")


def _read_json(path: str):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def snapshot_dates(slug: str) -> list:
    files = glob.glob(os.path.join(DATA_DIR, slug, "snapshots",
                                   "ranks_*.json"))
    return sorted(os.path.basename(f)[6:14] for f in files)


def load_snapshot(slug: str, date_yyyymmdd: str):
    return _read_json(os.path.join(DATA_DIR, slug, "snapshots",
                                   f"ranks_{date_yyyymmdd}.json"))


def latest_two(slug: str):
    dates = snapshot_dates(slug)
    today = load_snapshot(slug, dates[-1]) if dates else None
    prev = load_snapshot(slug, dates[-2]) if len(dates) >= 2 else None
    return today, prev


# ----------------------------------------------------------------------
def _momentum(rank_change: int, metric_growth: float | None,
              metric_value: float | None) -> float:
    """动能分：排名变化（每位 2 分）+ 指标环比增长（对数压缩，防月票大户碾压）。"""
    score = rank_change * 2.0
    if metric_growth is not None and metric_value:
        ratio = metric_growth / max(metric_value, 1)
        import math
        score += max(min(math.log1p(ratio * 10) * 8, 25), -10)
    return round(score, 1)


def compare_category(today_books: list, prev_books: list) -> dict:
    prev_index = {b["bid"]: b for b in prev_books}
    today_ids = {b["bid"] for b in today_books}

    new_books, dropped_books, movers = [], [], []
    metric_growth = []
    for i, b in enumerate(today_books):
        prev = prev_index.get(b["bid"])
        if not prev:
            new_books.append({"rank": i + 1, "title": b["title"],
                              "author": b["author"],
                              "subCategory": b.get("subCategory", "")})
            continue
        rc = prev["rank"] - (i + 1)
        mv = b.get("metric") or 0
        pv = prev.get("metric") or 0
        growth = (mv - pv) if (mv and pv) else None
        movers.append({
            "rank": i + 1, "title": b["title"], "author": b["author"],
            "rankChange": rc, "metric": mv,
            "metricGrowth": growth,
            "metricLabel": b.get("metricLabel", ""),
            "momentum": _momentum(rc, growth, mv),
        })
        if growth:
            metric_growth.append({"title": b["title"], "growth": growth})
    for b in prev_books:
        if b["bid"] not in today_ids:
            dropped_books.append({"title": b["title"],
                                  "subCategory": b.get("subCategory", "")})
    movers.sort(key=lambda m: m["momentum"], reverse=True)
    return {
        "new_books": new_books, "new_count": len(new_books),
        "dropped_books": dropped_books[:10], "dropped_count": len(dropped_books),
        "top_movers": movers[:8],
        "metric_growth": sorted(metric_growth, key=lambda x: -x["growth"])[:8],
        "first_day": False,
    }


# ----------------------------------------------------------------------
def keyword_heat(books: list, channel: str) -> list:
    words = (FEMALE_KEYWORDS if channel == "female" else MALE_KEYWORDS)
    counts = {}
    for b in books:
        text = b.get("intro", "") + "《" + b.get("title", "") + "》"
        for w in words:
            if w in text:
                counts[w] = counts.get(w, 0) + 1
    top = sorted(counts.items(), key=lambda x: -x[1])[:12]
    return [{"keyword": k, "count": v} for k, v in top]


def author_power(books: list) -> list:
    stats = {}
    for b in books:
        a = b.get("author") or "佚名"
        s = stats.setdefault(a, {"author": a, "books": 0, "top10": 0,
                                 "bestRank": 999, "titles": []})
        s["books"] += 1
        if b["rank"] <= 10:
            s["top10"] += 1
        s["bestRank"] = min(s["bestRank"], b["rank"])
        if len(s["titles"]) < 3:
            s["titles"].append(b["title"])
    out = sorted(stats.values(),
                 key=lambda s: (-s["books"], -s["top10"], s["bestRank"]))
    return [{**s, "bestRank": None if s["bestRank"] == 999 else s["bestRank"]}
            for s in out[:15] if s["books"] >= 2]


# ----------------------------------------------------------------------
def analyze_board(slug: str) -> dict | None:
    board = next((b for b in BOARDS if b["slug"] == slug), None)
    today, prev = latest_two(slug)
    if not today:
        return None

    today_cats = {c["name"]: c["books"] for c in today.get("categories", [])}
    prev_cats = {c["name"]: c["books"] for c in
                 (prev or {}).get("categories", [])}

    trends = {}
    for name, books in today_cats.items():
        if prev and name in prev_cats:
            trends[name] = compare_category(books, prev_cats[name])
        else:
            trends[name] = {
                "new_books": [], "new_count": 0, "dropped_books": [],
                "dropped_count": 0, "top_movers": [], "metric_growth": [],
                "first_day": True,
            }

    # 分类热度：指标总和 + Top10 占比
    category_heat = []
    for name, books in today_cats.items():
        total = sum(b.get("metric") or 0 for b in books)
        category_heat.append({
            "name": name, "count": len(books), "metric_total": total,
            "heat": total if total else len(books) * 100,
        })
    category_heat.sort(key=lambda x: -x["heat"])

    # 全部书籍（跨分类去重）
    seen, all_books = set(), []
    for books in today_cats.values():
        for b in books:
            if b["bid"] not in seen:
                seen.add(b["bid"])
                all_books.append(b)

    # 时间线（历史 Top3 + 关键指标）
    timeline = []
    for d in snapshot_dates(slug):
        snap = load_snapshot(slug, d)
        if not snap:
            continue
        first = next((c["books"][:3] for c in snap.get("categories", [])
                      if c["books"]), [])
        timeline.append({
            "date": datetime.strptime(d, "%Y%m%d").strftime("%Y-%m-%d"),
            "top3": [{"title": b["title"], "author": b["author"],
                      "metric": b.get("metric")} for b in first],
            "total_books": sum(len(c["books"]) for c in
                               snap.get("categories", [])),
        })

    return {
        "date": today["date"],
        "slug": slug,
        "board": today.get("board", {}),
        "total_books": len(all_books),
        "trends": trends,
        "category_heat": category_heat,
        "keyword_heat": keyword_heat(all_books,
                                     (board or {}).get("channel", "male")),
        "author_power": author_power(all_books),
        "timeline": timeline,
    }


# ----------------------------------------------------------------------
def cross_board_presence() -> list:
    """跨榜影响力：同一本书出现在多个榜单 → 合计动能 + 上榜数。"""
    agg = {}
    for board in enabled_boards():
        analysis = None
        dates = snapshot_dates(board["slug"])
        if not dates:
            continue
        snap = load_snapshot(board["slug"], dates[-1])
        prev = load_snapshot(board["slug"], dates[-2]) if len(dates) > 1 else {}
        if not snap:
            continue
        prev_ids = set()
        for c in (prev or {}).get("categories", []):
            prev_ids.update(b["bid"] for b in c["books"])
        for cat in snap.get("categories", []):
            if cat["name"] == "全部":
                continue  # 避免与分类重复计数
            for b in cat["books"]:
                e = agg.setdefault(b["bid"], {
                    "bid": b["bid"], "title": b["title"],
                    "author": b["author"], "category": b.get("category", ""),
                    "subCategory": b.get("subCategory", ""),
                    "cover": b.get("cover", ""),
                    "boards": [], "momentum": 0.0, "isNew": False,
                })
                if any(x["board"] == board["name"] for x in e["boards"]):
                    continue
                e["boards"].append({
                    "board": board["name"], "slug": board["slug"],
                    "category": cat["name"], "rank": b["rank"],
                    "metric": b.get("metric"),
                    "metricLabel": b.get("metricLabel", ""),
                })
                e["momentum"] += max(4, 34 - b["rank"]) / 4  # 排名贡献
                if b["bid"] not in prev_ids:
                    e["isNew"] = True
    out = [e for e in agg.values() if len(e["boards"]) >= 2]
    for e in out:
        e["boards"].sort(key=lambda x: x["rank"])
        e["momentum"] = round(e["momentum"] + (6 if e["isNew"] else 0), 1)
    out.sort(key=lambda e: (-len(e["boards"]), -e["momentum"]))
    return out[:30]
