"""
抓取编排 —— 遍历全部榜单、分类自动发现、Top N（跨页）、断点续跑。

数据流：
  data/<slug>/snapshots/ranks_YYYYMMDD.json   每日原始快照（增量追加）
  data/<slug>/task_state_YYYYMMDD.json        断点续跑状态
  data/categories/<slug>.json                 已发现的分类目录（缓存复用）
  data/last_run.json                          本次运行统计（看板状态栏）
"""
import json
import os
import random
import time
from datetime import datetime

from .config import enabled_boards, board_public_meta
from .fetcher import Fetcher
from .parser import discover_categories, finalize_metrics, parse_books

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

BASE_URL = "https://www.qidian.com/rank/{path}/"
CAT_URL = "https://www.qidian.com/rank/{path}/chn{chanid}/"
PAGE_URL = "https://www.qidian.com/rank/{path}/chn{chanid}/page{page}/"


def _write_json(path: str, obj) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


def _read_json(path: str):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _today() -> str:
    return datetime.now().strftime("%Y-%m-%d")


# ----------------------------------------------------------------------
def discover_board_categories(fetcher: Fetcher, board: dict) -> list:
    """抓榜单首页发现分类目录；结果缓存于 data/categories/<slug>.json。"""
    cache = os.path.join(DATA_DIR, "categories", f"{board['slug']}.json")
    cached = _read_json(cache)
    if cached and cached.get("date") == _today():
        return cached["categories"]

    html = fetcher.get(BASE_URL.format(path=board["path"]))
    if not html:
        if cached:
            print(f"  [CAT] {board['name']} 首页抓取失败，沿用缓存分类")
            return cached["categories"]
        return []
    cats = discover_categories(html)
    if cats:
        _write_json(cache, {"date": _today(), "categories": cats})
    return cats


def _fetch_category_top(fetcher: Fetcher, board: dict, chanid: str,
                        top_n: int) -> list:
    """抓单个分类的 Top N（每页 20 本，自动翻页）。

    chanid 为空 → 平铺榜（如女生频道）：首页即 base URL，翻页 /pageN/。
    """
    books, seen = [], set()
    pages = (top_n + 19) // 20
    for page in range(1, pages + 1):
        if chanid:
            url = (CAT_URL if page == 1 else PAGE_URL).format(
                path=board["path"], chanid=chanid, page=page)
        else:
            base = BASE_URL.format(path=board["path"])
            url = base if page == 1 else f"{base}page{page}/"
        html = fetcher.get(url)
        if not html:
            break
        page_books = parse_books(html)
        if not page_books:
            break
        for b in page_books:
            if b["bid"] not in seen:
                seen.add(b["bid"])
                books.append(b)
        if len(books) >= top_n:
            break
        time.sleep(random.uniform(0.3, 0.7))
    return finalize_metrics(books[:top_n])


# ----------------------------------------------------------------------
def scrape_board(fetcher: Fetcher, board: dict, top_n: int,
                 sleep_sec: float) -> dict:
    slug = board["slug"]
    date_str = datetime.now().strftime("%Y%m%d")
    board_dir = os.path.join(DATA_DIR, slug)
    snap_dir = os.path.join(board_dir, "snapshots")
    os.makedirs(snap_dir, exist_ok=True)
    output_file = os.path.join(snap_dir, f"ranks_{date_str}.json")
    state_file = os.path.join(board_dir, f"task_state_{date_str}.json")

    print(f"\n{'=' * 52}\n[榜单] {board['name']} ({slug})\n{'=' * 52}")

    categories = discover_board_categories(fetcher, board)
    if not categories:
        # 无分类导航 → 整榜作为单一伪分类
        categories = [{"chanid": "", "name": "全部"}]
    print(f"  分类目录：{len(categories)} 个 → "
          f"{'、'.join(c['name'] for c in categories[:8])}"
          f"{'…' if len(categories) > 8 else ''}")

    # 断点续跑
    done_cats, all_categories = [], []
    state = _read_json(state_file)
    if state:
        done_cats = state.get("completed", [])
        snap = _read_json(output_file)
        all_categories = (snap or {}).get("categories", [])
    todo = [c for c in categories if c["name"] not in done_cats]

    ok_count = err_count = 0
    for cat in todo:
        try:
            books = _fetch_category_top(fetcher, board, cat["chanid"], top_n)
        except Exception as e:  # noqa: BLE001
            books = []
            print(f"    ❌ {cat['name']} 抓取异常：{str(e)[:100]}")
        if books:
            all_categories.append({"name": cat["name"],
                                   "chanid": cat["chanid"],
                                   "books": books})
            done_cats.append(cat["name"])
            ok_count += 1
            # 每个分类落盘一次（增量快照，中断不丢数据）
            _write_json(output_file, {
                "date": _today(),
                "board": board_public_meta(board),
                "categories": all_categories,
            })
            _write_json(state_file, {"completed": done_cats})
            print(f"    ✅ {cat['name']}：{len(books)} 本已存档 "
                  f"({done_cats[-1] == cat['name'] and '' or ''}"
                  f"{len(done_cats)}/{len(categories)})")
        else:
            err_count += 1
            print(f"    ⚠️ {cat['name']}：0 本（跳过）")
        time.sleep(sleep_sec + random.uniform(0, 0.4))

    total_books = sum(len(c["books"]) for c in all_categories)
    print(f"  {'✅' if not err_count else '⚠️'} {board['name']} 完成："
          f"{len(all_categories)} 分类 / {total_books} 本"
          f"（失败 {err_count}）")
    return {"slug": slug, "name": board["name"], "ok": ok_count > 0
            and err_count == 0, "categories": len(all_categories),
            "books": total_books, "errors": err_count}


# ----------------------------------------------------------------------
def run_scraper(top_n: int = 30, sleep_sec: float = 0.8,
                only: list = None) -> list:
    deadline = int(os.environ.get("SCRAPE_DEADLINE_SEC", "0")) or None
    boards = enabled_boards()
    if only:
        boards = [b for b in boards if b["slug"] in only]
    if not boards:
        print("⚠️  没有启用的榜单")
        return []

    print(f"开始抓取起点 {len(boards)} 个榜单（每分类 Top {top_n}）…")
    fetcher = Fetcher()
    reports = []
    t0 = time.time()
    for board in boards:
        if deadline and (time.time() - t0) > deadline:
            print(f"  ⏰ 已达时间预算 {deadline}s，停止后续榜单，保留已抓取数据")
            break
        try:
            reports.append(scrape_board(fetcher, board, top_n, sleep_sec))
        except Exception as e:  # noqa: BLE001
            print(f"  ❌ 榜单 {board['name']} 出错：{e}")
            reports.append({"slug": board["slug"], "name": board["name"],
                            "ok": False, "categories": 0, "books": 0,
                            "errors": 1})

    ok = sum(1 for r in reports if r["ok"])
    _write_json(os.path.join(DATA_DIR, "last_run.json"), {
        "finished_at": datetime.now().isoformat(timespec="seconds"),
        "duration_sec": round(time.time() - t0, 1),
        "boards_ok": ok, "boards_total": len(reports),
        "total_books": sum(r["books"] for r in reports),
        "total_categories": sum(r["categories"] for r in reports),
        "reports": reports,
    })
    print(f"\n{'✅' if ok == len(reports) else '⚠️'} {ok}/{len(reports)} "
          f"个榜单抓取成功，共 "
          f"{sum(r['books'] for r in reports)} 本书，"
          f"耗时 {time.time() - t0:.0f}s。")
    if ok == 0:
        # 全部失败（疑似 WAF 拦截）：抛错让 CI 步骤失败，避免提交/部署空数据。
        raise RuntimeError("全部榜单抓取失败（疑似被 WAF 拦截），不提交空数据")
    return reports
