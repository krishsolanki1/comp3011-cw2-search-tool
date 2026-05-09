"""Search module — queries the inverted index for matching pages."""


class Searcher:
    """Searches the inverted index for one or more query terms."""

    def __init__(self, index: dict[str, dict]):
        self.index = index

    def find(self, query: str) -> list[dict]:
        """Return ranked list of results for the given query string."""
        raise NotImplementedError

    def print_word(self, word: str) -> None:
        """Print frequency and location data for a single word."""
        raise NotImplementedError
