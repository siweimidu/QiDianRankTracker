"""
AI 风向分析 —— OpenAI 兼容 API（纯 requests 实现，零额外依赖）。

  * 标准 Chat Completions 协议：Moonshot / DeepSeek / GLM / GPT / 自建均可
  * 批量并发 + 单点失败不影响整体
  * 未配置或失败时自动回退规则文案
"""
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor

import requests

API_BASE_URL = os.environ.get("API_BASE_URL", "").rstrip("/")
API_KEY = os.environ.get("API_KEY", "")
API_MODEL = os.environ.get("API_MODEL", "gpt-4o-mini")


def ai_available() -> bool:
    return bool(API_BASE_URL and API_KEY)


def chat(prompt: str, max_tokens: int = 500) -> str:
    resp = requests.post(
        f"{API_BASE_URL}/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}",
                 "Content-Type": "application/json"},
        json={
            "model": API_MODEL,
            "messages": [
                {"role": "system", "content": (
                    "你是一位资深网文行业分析师，为起点中文网榜单撰写趋势速评。"
                    "要求：观点犀利、有数据支撑、给作者/编辑可执行的洞察；"
                    "控制在 120 字以内；直接输出正文，不要客套。")},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.6,
            "max_tokens": max_tokens,
        }, timeout=90)
    resp.raise_for_status()
    data = resp.json()
    return (data["choices"][0]["message"]["content"] or "").strip()


def safe_chat(prompt: str, fallback: str) -> str:
    if not ai_available():
        return fallback
    try:
        out = chat(prompt)
        return out or fallback
    except Exception as e:  # noqa: BLE001
        print(f"  [AI] 调用失败，规则文案兜底：{str(e)[:120]}")
        return fallback


# ----------------------------------------------------------------------
# 规则兜底文案
# ----------------------------------------------------------------------
def rule_summary(board_name: str, cat_name: str, trend: dict) -> str:
    parts = []
    if trend.get("first_day"):
        return (f"【{board_name}·{cat_name}】基线首日：已锁定当前榜单结构，"
                f"明日起输出新上榜/掉榜/黑马对比信号。")
    if trend.get("new_count"):
        parts.append(f"{trend['new_count']} 本新上榜")
    if trend.get("dropped_count"):
        parts.append(f"{trend['dropped_count']} 本掉榜")
    movers = trend.get("top_movers") or []
    if movers and movers[0].get("momentum", 0) > 0:
        m = movers[0]
        parts.append(f"《{m['title']}》动能 {m['momentum']} 分领跑")
    growth = trend.get("metric_growth") or []
    if growth:
        g = growth[0]
        parts.append(f"《{g['title']}》指标 +{g['growth']}")
    if not parts:
        parts.append("榜单结构稳定，头部固若金汤")
    return f"【{board_name}·{cat_name}】" + "；".join(parts) + "。"


def rule_brief(board_analyses: list) -> str:
    analyses = [a for a in board_analyses if a]
    if not analyses:
        return "今日暂无数据。"
    if all(a.get("trends", {}).get("全部", {}).get("first_day")
           for a in analyses if a.get("trends")):
        total = sum(a.get("total_books", 0) for a in analyses)
        return (f"今日起点 {len(analyses)} 个榜单完成基线建立，"
                f"共追踪 {total} 条记录。明日起将输出新上榜/掉榜/"
                f"跨榜黑马与赛道热度信号。")
    total_books = sum(a.get("total_books", 0) for a in analyses)
    total_new = sum(next(iter(a["trends"].values()), {}).get("new_count", 0)
                    for a in analyses if a.get("trends"))
    lines = [f"今日起点 {len(analyses)} 个榜单共追踪 {total_books} 条记录，"
             f"全站换血 {total_new} 本。"]
    highlights = []
    for a in analyses:
        if not a:
            continue
        for cat, t in (a.get("trends") or {}).items():
            for m in (t.get("top_movers") or [])[:1]:
                if m.get("momentum", 0) >= 8:
                    highlights.append(
                        f"《{m['title']}》在{a['board'].get('name', '')}"
                        f"{cat}榜动能 {m['momentum']}")
    if highlights:
        lines.append("关注：" + "；".join(highlights[:3]) + "。")
    lines.append("付费盘（月票/畅销）与流量盘（追读/收藏）的头部重合度，"
                 "决定新书突围的最优路径。")
    return "".join(lines)


# ----------------------------------------------------------------------
# Prompt 构建
# ----------------------------------------------------------------------
def build_ai_prompt(board_name: str, cat_name: str, cat: dict,
                    trend: dict) -> str:
    books = cat.get("books", [])[:15]
    lines = []
    for i, b in enumerate(books):
        metric = (f"{b.get('metricLabel', '')} {b.get('metric')}"
                  if b.get("metric") is not None else "")
        lines.append(f"{i + 1}. 《{b['title']}》{b['author']} "
                     f"[{b.get('subCategory') or b.get('category', '?')}] "
                     f"{metric}")
    new_b = "、".join(f"《{n['title']}》(第{n['rank']}名)"
                      for n in trend.get("new_books", [])[:5]) or "无"
    drop_b = "、".join(f"《{d['title']}》"
                       for d in trend.get("dropped_books", [])[:5]) or "无"
    movers = trend.get("top_movers", [])[:5]
    move_b = "、".join(
        f"《{m['title']}》{'↑' if m.get('rankChange', 0) > 0 else '↓'}"
        f"{abs(m.get('rankChange', 0))}位"
        + (f"(+{m['metricGrowth']})" if m.get("metricGrowth") else "")
        for m in movers if m.get("rankChange")) or "无明显变动"

    return f"""起点中文网「{board_name} · {cat_name}」今日榜单：

{chr(10).join(lines)}

新上榜：{new_b}
掉榜：{drop_b}
名次变动：{move_b}

请输出一条 120 字以内的趋势速评：聚焦题材风向、黑马信号、竞争格局变化，
并给作者/编辑一条可执行建议。"""


def build_brief_prompt(board_analyses: list) -> str:
    sec = []
    for a in board_analyses:
        if not a:
            continue
        bname = a.get("board", {}).get("name", "")
        heat = "、".join(f"{c['name']}"
                         for c in (a.get("category_heat") or [])[:4])
        allc = next(iter((a.get("trends") or {}).values()), {})
        sec.append(f"【{bname}】热点分类：{heat or '无'}；"
                   f"新上榜 {allc.get('new_count', 0)} 本，"
                   f"掉榜 {allc.get('dropped_count', 0)} 本")
    return f"""以下是起点中文网今日各榜单摘要：

{chr(10).join(sec)}

请写一段 150 字以内的「今日起点风向日报」：
1) 一句话概括大盘情绪；
2) 指出 1~2 个正在走强的题材赛道；
3) 点出 1~2 本值得关注的黑马及其信号；
4) 给写作者一条选题建议。"""


# ----------------------------------------------------------------------
def summarize_brief(board_analyses: list) -> str:
    prompt = build_brief_prompt(board_analyses)
    return safe_chat(prompt, rule_brief(board_analyses))


def parallel_summarize(jobs: list, max_workers: int = 4) -> dict:
    """jobs: [{'key','prompt','fallback'}] → {key: summary}"""
    results = {}

    def _run(job):
        return job["key"], safe_chat(job["prompt"], job["fallback"])

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        for key, text in pool.map(_run, jobs):
            results[key] = text
    return results
