"""Indexer module — builds an inverted index from crawled page data."""


class Indexer:
    """Builds and holds an inverted index mapping words to page locations."""

    def __init__(self):
        self.index: dict[str, dict] = {}

    def build(self, pages: list[dict]) -> None:
        """Build the inverted index from a list of page dicts."""
        raise NotImplementedError

    def get(self, word: str) -> dict:
        """Return index entry for a word, or empty dict if not found."""
        return self.index.get(word.lower(), {})
