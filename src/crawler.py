"""Web crawler — fetches pages from quotes.toscrape.com following pagination."""

import time
from collections.abc import Callable
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"
USER_AGENT = "COMP3011-SearchTool/1.0 (educational crawler)"


class Crawler:
    """Crawls pages from the target site, following 'next' pagination links."""

    def __init__(
        self,
        base_url: str = BASE_URL,
        delay_seconds: float = 6,
        timeout: int = 10,
        session: requests.Session | None = None,
        sleeper: Callable[[float], None] | None = None,
    ) -> None:
        self.base_url = base_url
        self.delay_seconds = delay_seconds
        self.timeout = timeout
        self._session = session or requests.Session()
        self._session.headers.update({"User-Agent": USER_AGENT})
        self._sleep = sleeper if sleeper is not None else time.sleep
        self._allowed_host = urlparse(base_url).netloc

    def crawl(self) -> dict[str, str]:
        """Crawl pages starting from base_url and return {url: html} mapping."""
        pages: dict[str, str] = {}
        url: str | None = self.base_url

        while url:
            if url in pages:
                break

            html = self._fetch(url)
            if html is None:
                break

            pages[url] = html

            next_url = self._next_url(html, url)
            if next_url and next_url not in pages:
                self._sleep(self.delay_seconds)
                url = next_url
            else:
                break

        return pages

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _fetch(self, url: str) -> str | None:
        """GET a URL and return the response text, or None on error."""
        try:
            response = self._session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.text
        except requests.RequestException as exc:
            print(f"[crawler] request failed for {url}: {exc}")
            return None

    def _next_url(self, html: str, current_url: str) -> str | None:
        """Parse the HTML for a 'next' pagination link and return its absolute URL."""
        soup = BeautifulSoup(html, "html.parser")
        next_li = soup.select_one("li.next > a")
        if not next_li:
            return None

        href = next_li.get("href", "")
        absolute = urljoin(current_url, href)

        # Stay within the allowed domain
        if urlparse(absolute).netloc != self._allowed_host:
            return None

        return absolute
