"""访谈爬取器：从 THBWiki / GitHub / 二轩目广播 拉取原始访谈数据"""

import time

from config import RAW_DIR, INTERVIEW_URLS, GITHUB_INTERVIEWS, NIKENME_URL
from parsers import InterviewParser


class InterviewCrawler:
    """访谈数据爬取器：抓取 → 缓存 → 解析"""

    def __init__(self):
        self.parser = InterviewParser()

    # ── URL 抓取 ──────────────────────────────────────

    @staticmethod
    def fetch_url(url: str) -> str:
        """抓取 URL 内容"""
        import urllib.request
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        })
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read().decode("utf-8", errors="replace")

    # ── 带缓存的抓取 ─────────────────────────────────

    def fetch_with_cache(self, source_id: str, url: str, suffix: str) -> str | None:
        """带本地缓存的抓取，返回内容或 None"""
        raw_file = RAW_DIR / f"{source_id}{suffix}"
        if raw_file.exists():
            print(f"  [cached] {source_id}")
            return raw_file.read_text(encoding="utf-8")

        print(f"  [fetching] {source_id}")
        try:
            content = self.fetch_url(url)
            raw_file.write_text(content, encoding="utf-8")
            time.sleep(0.5)
            return content
        except Exception as e:
            print(f"  [error] {source_id}: {e}")
            return None

    # ── THBWiki 爬取 ─────────────────────────────────

    def fetch_thbwiki_interviews(self) -> list:
        """爬取 THBWiki HTML 访谈源，返回语录列表"""
        all_quotes = []
        for source_id, url in INTERVIEW_URLS:
            content = self.fetch_with_cache(source_id, url, ".html")
            if content:
                quotes = self.parser.parse_html_auto(content, source_id)
                all_quotes.extend(quotes)
                print(f"    → {len(quotes)} quotes")
        return all_quotes

    # ── GitHub Markdown 爬取 ──────────────────────────

    def fetch_github_interviews(self) -> list:
        """爬取 GitHub Markdown 访谈源，返回语录列表"""
        all_quotes = []
        for source_id, url in GITHUB_INTERVIEWS:
            content = self.fetch_with_cache(source_id, url, ".md")
            if content:
                quotes = self.parser.parse_markdown_interview(content, source_id)
                all_quotes.extend(quotes)
                print(f"    → {len(quotes)} quotes")
        return all_quotes

    # ── 二轩目广播爬取 ────────────────────────────────

    def fetch_nikenme_radio(self) -> list:
        """爬取二轩目广播内容，返回语录列表"""
        content = self.fetch_with_cache("nikenme-radio", NIKENME_URL, ".html")
        if not content:
            return []

        quotes = self.parser.parse_nikenme_radio(content, "nikenme")
        print(f"    → {len(quotes)} quotes from nikenme radio")
        return quotes

    # ── 主入口 ──────────────────────────────────────

    def fetch_all(self) -> list:
        """爬取所有访谈源，返回语录列表"""
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        all_quotes = []

        all_quotes.extend(self.fetch_thbwiki_interviews())
        all_quotes.extend(self.fetch_github_interviews())
        all_quotes.extend(self.fetch_nikenme_radio())

        return all_quotes


# ── 模块级便捷函数（向后兼容）──────────────────────────────

_crawler = InterviewCrawler()

def fetch_interviews():
    """向后兼容的模块级入口"""
    return _crawler.fetch_all()
