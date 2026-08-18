"""
高速抓取会话 —— 复用 WAF Cookie 的纯 HTTP 抓取。

优化点（相对 Playwright 逐页抓取）：
  * 单次浏览器握手后全程 requests，单页耗时 ~0.5s（浏览器 ~5s）
  * 挑战识别：202 / probe.js / WafCaptcha / 空壳页 自动触发重新握手
  * 指数退避 + 全局限速（默认 0.55s + 抖动），对站点友好
"""
import random
import time

import requests

from .browser import UA, handshake

CHALLENGE_MARKS = ("probe.js", "WafCaptcha", "TCaptcha")
MIN_INTERVAL = 0.55


class Fetcher:
    """带 WAF 自愈能力的 HTTP 抓取器。"""

    def __init__(self, min_interval: float = MIN_INTERVAL, verbose: bool = True):
        self.min_interval = min_interval
        self.verbose = verbose
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": UA,
            "Accept": ("text/html,application/xhtml+xml,application/xml;"
                       "q=0.9,*/*;q=0.8"),
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Connection": "keep-alive",
        })
        self._last_ts = 0.0
        self._refresh_cookies()

    # ------------------------------------------------------------------
    def _refresh_cookies(self):
        cookies = handshake(verbose=self.verbose)
        self.session.cookies.update(cookies)

    @staticmethod
    def _is_challenge(resp) -> bool:
        """真实内容标记优先：榜单页 SSR HTML 必含书卡/分类导航。

        注意：正常页面也会包含 TCaptcha 脚本（加入书架按钮），
        所以不能仅凭关键字判定，必须先看真实内容标记。
        """
        if resp.status_code == 202:
            return True
        body = resp.text
        if len(body) < 1500:
            return True
        for marker in ("book-mid-info", "data-chanid", "li data-rid"):
            if marker in body:
                return False
        return any(m in body[:4000]
                   for m in ("probe.js", "WafCaptcha", "var seqid"))

    # ------------------------------------------------------------------
    def get(self, url: str, retries: int = 3, timeout: int = 20) -> str | None:
        """GET 并返回 HTML 文本；挑战自动重握手重试。"""
        for attempt in range(retries + 1):
            self._throttle()
            try:
                resp = self.session.get(url, timeout=timeout)
            except requests.RequestException as e:
                if self.verbose:
                    print(f"    [HTTP] 网络错误：{str(e)[:100]}")
                time.sleep(2 + attempt * 2)
                continue
            if resp.status_code == 200 and not self._is_challenge(resp):
                return resp.text
            if self.verbose:
                tag = ("WAF挑战" if self._is_challenge(resp)
                       else f"HTTP {resp.status_code}")
                print(f"    [HTTP] {tag}，尝试重新握手（{attempt + 1}）")
            try:
                self._refresh_cookies()
            except RuntimeError as e:
                if attempt >= retries:
                    print(f"    [HTTP] 放弃：{e}")
                    return None
            time.sleep(1.5 + attempt * 2)
        return None

    def _throttle(self):
        wait = self.min_interval - (time.time() - self._last_ts)
        if wait > 0:
            time.sleep(wait + random.uniform(0, 0.25))
        self._last_ts = time.time()
