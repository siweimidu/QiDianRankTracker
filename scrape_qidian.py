#!/usr/bin/env python3
"""
起点榜单抓取 CLI 入口。

用法：
  python scrape_qidian.py                    # 抓取全部 16 个榜单（每分类 Top 30）
  python scrape_qidian.py --top 50           # 自定义 Top N
  python scrape_qidian.py --only yuepiao recom   # 只抓指定榜单
  python scrape_qidian.py --build            # 抓取后顺带构建看板数据
  python scrape_qidian.py --sleep 0.5        # 更快（分类间隔秒数，默认 0.8）
"""
import argparse

from qd_tracker.scrape import run_scraper


def main():
    parser = argparse.ArgumentParser(description="起点中文网榜单抓取器")
    parser.add_argument("--top", type=int, default=30, help="每分类抓取 Top N")
    parser.add_argument("--only", nargs="*", default=None,
                        help="只抓指定 slug 的榜单")
    parser.add_argument("--sleep", type=float, default=0.8,
                        help="分类之间的间隔秒数")
    parser.add_argument("--build", action="store_true",
                        help="抓取后立即构建看板数据")
    args = parser.parse_args()

    print("开始执行起点多榜单抓取计划…")
    reports = run_scraper(top_n=args.top, sleep_sec=args.sleep,
                          only=args.only)
    ok = sum(1 for r in reports if r["ok"])
    print(f"\n{'✅' if ok == len(reports) else '⚠️'} "
          f"{ok}/{len(reports)} 个榜单抓取成功。")

    if args.build:
        from qd_tracker.build import build_all
        build_all()


if __name__ == "__main__":
    main()
