"""
WAF 握手模块 —— 用 Playwright 隐身浏览器通过起点腾讯云 WAF。

起点 www 站被腾讯云 WAF 保护：
  * 纯 HTTP 请求 → 202 + probe.js JS 挑战
  * 无补丁的自动化浏览器 → TCaptcha 验证码
  * 隐身补丁（隐藏 navigator.webdriver 等）+ 自动化控制关闭 → 正常放行

本模块只负责「过门」拿 Cookie，之后的批量抓取全部交给 fetcher 的
纯 HTTP 会话（快 5~8 倍）。
"""
import sys
import time

HANDSHAKE_URL = "https://www.qidian.com/rank/yuepiao/"

# 隐身补丁：仅覆盖 WAF 检测的高频指纹项，克制而不臃肿
STEALTH_INIT = """
Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
window.chrome = window.chrome || { runtime: {} };
Object.defineProperty(navigator, 'languages', {get: () => ['zh-CN','zh','en']});
Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4,5]});
"""

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")


def _launch(p):
    """优先系统 Edge/Chrome，回退 Playwright 自带 Chromium。"""
    for channel in ("msedge", "chrome"):
        try:
            return p.chromium.launch(
                headless=True, channel=channel,
                args=["--disable-blink-features=AutomationControlled",
                      "--disable-dev-shm-usage"])
        except Exception:
            continue
    return p.chromium.launch(
        headless=True,
        args=["--disable-blink-features=AutomationControlled",
              "--disable-dev-shm-usage"])


def handshake(verbose: bool = True) -> dict:
    """通过 WAF 并返回可用 Cookie 字典。失败抛出 RuntimeError。"""
    from playwright.sync_api import sync_playwright, Error as PWError

    last_err = ""
    for attempt in range(3):
        try:
            with sync_playwright() as p:
                browser = _launch(p)
                ctx = browser.new_context(
                    user_agent=UA, locale="zh-CN",
                    viewport={"width": 1440, "height": 900},
                )
                ctx.add_init_script(STEALTH_INIT)
                page = ctx.new_page()
                page.goto(HANDSHAKE_URL, timeout=45000,
                          wait_until="domcontentloaded")
                # 轮询等待 WAF 挑战自动完成（出现真实内容）
                for _ in range(12):
                    time.sleep(1.5)
                    try:
                        ok = page.eval_on_selector_all(
                            "li[data-rid], a[data-chanid]",
                            "els => els.length")
                    except Exception:
                        ok = 0
                    if ok:
                        cookies = {c["name"]: c["value"]
                                   for c in ctx.cookies()
                                   if "qidian" in c.get("domain", "")}
                        browser.close()
                        if verbose:
                            print(f"  [WAF] 握手成功（第 {attempt + 1} 次尝试），"
                                  f"取得 {len(cookies)} 枚 Cookie")
                        return cookies
                html = page.content()
                browser.close()
                last_err = ("captcha" if "TCaptcha" in html or "WafCaptcha"
                            in html else f"timeout, html={len(html)}B")
        except (PWError, Exception) as e:  # noqa: BLE001
            last_err = str(e)[:160]
        if verbose:
            print(f"  [WAF] 握手失败（{last_err}），退避重试…")
        time.sleep(3 + attempt * 4)
    raise RuntimeError(f"无法通过起点 WAF：{last_err}")


if __name__ == "__main__":
    ck = handshake()
    print(sorted(ck))
    print(f"cookies={len(ck)}", file=sys.stderr)
