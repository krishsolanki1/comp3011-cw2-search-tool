"""Indexer -- extracts text, tokenises it, and builds an inverted index."""

import re

from bs4 import BeautifulSoup

# Tags whose content should never be indexed
_SKIP_TAGS = {"script", "style", "head", "meta", "noscript"}


def extract_visible_text(html: str) -> str:
    """Return the visible human-readable text from an HTML string."""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup.find_all(_SKIP_TAGS):
        tag.decompose()
    return soup.get_text(separator=" ")


def tokenize(text: str) -> list[str]:
    """Lowercase and split text into alphanumeric tokens, dropping punctuation."""
    return re.findall(r"[a-z0-9]+", text.lower())


class InvertedIndex:
    """
    Inverted index mapping words to per-document frequency and position data.

    Index structure::

        {
            "word": {
                "https://example.com/": {
                    "frequency": 3,
                    "positions": [4, 18, 42]
                }
            }
        }

    Document metadata structure::

        {
            "https://example.com/": {
                "word_count": 123,
                "title": "Page Title"
            }
        }

    Complexity notes:
    - Word lookup (get_word) is O(1) average -- plain dictionary access.
    - Building the index is O(T) where T is the total number of tokens across
      all documents.
    - Serialisation (to_dict/from_dict) is O(V * D) where V is vocabulary size
      and D is number of documents.
    """

    def __init__(self) -> None:
        self._index: dict[str, dict[str, dict]] = {}
        self._docs: dict[str, dict] = {}
        self.built_at: str | None = None  # ISO-8601 timestamp, set by main on build

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def add_document(self, url: str, html: str) -> None:
        """Index a single page given its URL and raw HTML."""
        soup = BeautifulSoup(html, "html.parser")
        title_tag = soup.find("title")
        title = title_tag.get_text(strip=True) if title_tag else ""

        text = extract_visible_text(html)
        tokens = tokenize(text)

        self._docs[url] = {"word_count": len(tokens), "title": title}

        for position, word in enumerate(tokens):
            entry = self._index.setdefault(word, {})
            if url not in entry:
                entry[url] = {"frequency": 0, "positions": []}
            entry[url]["frequency"] += 1
            entry[url]["positions"].append(position)

    def build_from_pages(self, pages: dict[str, str]) -> None:
        """Build the index from a {url: html} mapping (e.g. crawler output)."""
        for url, html in pages.items():
            self.add_document(url, html)

    def get_word(self, word: str) -> dict:
        """Return index entry for a word, or an empty dict if not present.

        Complexity: O(1) average (dictionary lookup).
        """
        return self._index.get(word.lower(), {})

    def to_dict(self) -> dict:
        """Serialise the full index and document metadata to a plain dict."""
        result: dict = {"index": self._index, "docs": self._docs}
        if self.built_at is not None:
            result["built_at"] = self.built_at
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "InvertedIndex":
        """Reconstruct an InvertedIndex from a dict produced by to_dict()."""
        obj = cls()
        obj._index = data.get("index", {})
        obj._docs = data.get("docs", {})
        obj.built_at = data.get("built_at")
        return obj
