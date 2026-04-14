"""Search engine — print word entries and find pages matching query terms."""

import re

from src.indexer import InvertedIndex


def normalise_query(query: str) -> list[str]:
    """Lowercase and split a query string into individual word tokens."""
    return re.findall(r"[a-z0-9]+", query.lower())


class SearchEngine:
    """Queries an InvertedIndex to support print-word and find operations."""

    def __init__(self, index: InvertedIndex) -> None:
        self._index = index

    # ------------------------------------------------------------------
    # Core query methods
    # ------------------------------------------------------------------

    def get_word_entry(self, word: str) -> dict:
        """Return the raw index entry for a single word."""
        return self._index.get_word(word)

    def find(self, query: str) -> list[dict]:
        """Return pages containing ALL query terms, ranked by combined frequency.

        Each result is a dict::

            {
                "url": "...",
                "score": 5,
                "matched_terms": ["good", "friends"],
                "frequencies": {"good": 3, "friends": 2}
            }
        """
        terms = normalise_query(query)
        if not terms:
            return []

        # Collect per-term entries
        term_entries: dict[str, dict] = {t: self._index.get_word(t) for t in terms}

        # Candidate URLs must appear in every term's entry (AND logic)
        candidate_urls: set[str] | None = None
        for entry in term_entries.values():
            urls = set(entry.keys())
            candidate_urls = urls if candidate_urls is None else candidate_urls & urls

        if not candidate_urls:
            return []

        results: list[dict] = []
        for url in candidate_urls:
            frequencies = {t: term_entries[t][url]["frequency"] for t in terms}
            results.append(
                {
                    "url": url,
                    "score": sum(frequencies.values()),
                    "matched_terms": terms,
                    "frequencies": frequencies,
                }
            )

        results.sort(key=lambda r: r["score"], reverse=True)
        return results

    # ------------------------------------------------------------------
    # Formatting helpers (used by main.py for human-readable CLI output)
    # ------------------------------------------------------------------

    def format_word_entry(self, word: str) -> str:
        """Return a human-readable string for a single word's index entry."""
        entry = self.get_word_entry(word)
        if not entry:
            return f'No index entry found for "{word}".'

        lines = [f'Word: "{word}"', f"  Found on {len(entry)} page(s):"]
        for url, data in entry.items():
            lines.append(f"    {url}")
            lines.append(f"      frequency : {data['frequency']}")
            lines.append(f"      positions : {data['positions']}")
        return "\n".join(lines)

    def format_find_results(self, query: str) -> str:
        """Return a human-readable string summarising find results."""
        terms = normalise_query(query)
        if not terms:
            return "Please provide at least one search term."

        results = self.find(query)
        if not results:
            return f'No pages found containing all of: {", ".join(terms)}.'

        lines = [
            f"Found {len(results)} page(s) for query: {', '.join(terms)}",
            "",
        ]
        for rank, result in enumerate(results, start=1):
            lines.append(f"  {rank}. {result['url']}")
            lines.append(f"     score : {result['score']}")
            for term, freq in result["frequencies"].items():
                lines.append(f"     {term!r:12s}: {freq} occurrence(s)")
        return "\n".join(lines)
