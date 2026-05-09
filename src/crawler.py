"""Web crawler module — fetches and parses pages from the target website."""


class Crawler:
    """Crawls pages from a given base URL."""

    def __init__(self, base_url: str, max_pages: int = 50):
        self.base_url = base_url
        self.max_pages = max_pages

    def crawl(self) -> list[dict]:
        """Crawl pages and return a list of page dicts with url and text."""
        raise NotImplementedError
