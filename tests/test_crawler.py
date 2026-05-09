"""Unit tests for the Crawler class. No live network requests; no real sleeps."""

from unittest.mock import MagicMock

import requests

from src.crawler import Crawler

# ---------------------------------------------------------------------------
# HTML fixtures
# ---------------------------------------------------------------------------

PAGE_1 = """
<html><body>
  <div class="quote"><span class="text">Quote one</span></div>
  <ul class="pager"><li class="next"><a href="/page/2/">Next</a></li></ul>
</body></html>
"""

PAGE_2 = """
<html><body>
  <div class="quote"><span class="text">Quote two</span></div>
</body></html>
"""

EXTERNAL_NEXT = """
<html><body>
  <ul class="pager"><li class="next"><a href="https://evil.com/page/2/">Next</a></li></ul>
</body></html>
"""


def _make_response(text: str, status: int = 200) -> MagicMock:
    resp = MagicMock()
    resp.text = text
    resp.status_code = status
    resp.raise_for_status = MagicMock()
    return resp


def _no_sleep(_seconds: float) -> None:
    pass


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_crawl_single_page_no_next():
    """Crawler stops when there is no next link."""
    session = MagicMock()
    session.get.return_value = _make_response(PAGE_2)

    crawler = Crawler(
        base_url="https://quotes.toscrape.com/",
        session=session,
        sleeper=_no_sleep,
    )
    result = crawler.crawl()

    assert len(result) == 1
    assert "https://quotes.toscrape.com/" in result


def test_crawl_follows_next_link():
    """Crawler follows the 'next' pagination link to a second page."""
    session = MagicMock()
    session.get.side_effect = [
        _make_response(PAGE_1),
        _make_response(PAGE_2),
    ]

    crawler = Crawler(
        base_url="https://quotes.toscrape.com/",
        session=session,
        sleeper=_no_sleep,
    )
    result = crawler.crawl()

    assert len(result) == 2
    assert "https://quotes.toscrape.com/" in result
    assert "https://quotes.toscrape.com/page/2/" in result


def test_crawl_collects_html_content():
    """Returned dict maps each URL to its raw HTML string."""
    session = MagicMock()
    session.get.side_effect = [
        _make_response(PAGE_1),
        _make_response(PAGE_2),
    ]

    crawler = Crawler(
        base_url="https://quotes.toscrape.com/",
        session=session,
        sleeper=_no_sleep,
    )
    result = crawler.crawl()

    assert "Quote one" in result["https://quotes.toscrape.com/"]
    assert "Quote two" in result["https://quotes.toscrape.com/page/2/"]


def test_crawl_avoids_duplicates():
    """Crawler does not revisit a URL it has already fetched."""
    # PAGE_1's next link points back to the base URL — should stop, not loop.
    looping_page = """
    <html><body>
      <ul class="pager">
        <li class="next"><a href="/">Next</a></li>
      </ul>
    </body></html>
    """
    session = MagicMock()
    session.get.return_value = _make_response(looping_page)

    crawler = Crawler(
        base_url="https://quotes.toscrape.com/",
        session=session,
        sleeper=_no_sleep,
    )
    result = crawler.crawl()

    # Should only fetch the base URL once
    assert session.get.call_count == 1
    assert len(result) == 1


def test_crawl_sleeps_between_requests():
    """Sleeper is called exactly once between the two page fetches."""
    sleep_calls: list[float] = []

    def recording_sleeper(seconds: float) -> None:
        sleep_calls.append(seconds)

    session = MagicMock()
    session.get.side_effect = [
        _make_response(PAGE_1),
        _make_response(PAGE_2),
    ]

    crawler = Crawler(
        base_url="https://quotes.toscrape.com/",
        delay_seconds=6,
        session=session,
        sleeper=recording_sleeper,
    )
    crawler.crawl()

    assert len(sleep_calls) == 1
    assert sleep_calls[0] == 6


def test_crawl_no_sleep_on_single_page():
    """Sleeper is never called when there is only one page."""
    sleep_calls: list[float] = []

    def recording_sleeper(seconds: float) -> None:
        sleep_calls.append(seconds)

    session = MagicMock()
    session.get.return_value = _make_response(PAGE_2)

    crawler = Crawler(
        base_url="https://quotes.toscrape.com/",
        session=session,
        sleeper=recording_sleeper,
    )
    crawler.crawl()

    assert sleep_calls == []


def test_crawl_handles_request_exception_gracefully():
    """A network error on the first request returns an empty dict, not a crash."""
    session = MagicMock()
    session.get.side_effect = requests.ConnectionError("unreachable")

    crawler = Crawler(
        base_url="https://quotes.toscrape.com/",
        session=session,
        sleeper=_no_sleep,
    )
    result = crawler.crawl()

    assert result == {}


def test_crawl_stops_after_mid_crawl_error():
    """A network error on the second request returns only the first page."""
    session = MagicMock()
    session.get.side_effect = [
        _make_response(PAGE_1),
        requests.ConnectionError("page 2 unreachable"),
    ]

    crawler = Crawler(
        base_url="https://quotes.toscrape.com/",
        session=session,
        sleeper=_no_sleep,
    )
    result = crawler.crawl()

    assert len(result) == 1
    assert "https://quotes.toscrape.com/" in result


def test_crawl_ignores_external_domain_next_link():
    """A 'next' link pointing outside the allowed domain is not followed."""
    session = MagicMock()
    session.get.return_value = _make_response(EXTERNAL_NEXT)

    crawler = Crawler(
        base_url="https://quotes.toscrape.com/",
        session=session,
        sleeper=_no_sleep,
    )
    result = crawler.crawl()

    assert len(result) == 1
    fetched_urls = [str(call.args[0]) for call in session.get.call_args_list]
    assert not any("evil.com" in u for u in fetched_urls)


def test_crawler_sends_user_agent():
    """The session is configured with a non-empty User-Agent header."""
    crawler = Crawler(base_url="https://quotes.toscrape.com/", sleeper=_no_sleep)
    assert "User-Agent" in crawler._session.headers
    assert crawler._session.headers["User-Agent"] != ""
