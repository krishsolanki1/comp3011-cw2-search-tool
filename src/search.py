"""Search engine -- TF-IDF ranked search with proximity scoring and query suggestions."""

import difflib
import math
import re

from src.indexer import InvertedIndex


def normalise_query(query: str) -> list[str]:
    """Lowercase and split a query string into individual word tokens."""
    return re.findall(r"[a-z0-9]+", query.lower())


class SearchEngine:
    """
    Queries an InvertedIndex using TF-IDF ranking with a proximity bonus.

    Ranking formula
    ---------------
    For each candidate document and each query term t:

        tf(t, doc)  = raw frequency of t in doc
        idf(t)      = log((1 + N) / (1 + df(t))) + 1
                      where N  = total number of indexed documents
                            df = number of documents containing t
                      The +1 smoothing prevents division by zero and keeps
                      IDF >= 1 even for terms appearing in every document.

        tfidf_score = sum( tf(t, doc) * idf(t) )  for all query terms t

    Proximity bonus (multi-word queries only)
    -----------------------------------------
    When a query has two or more terms, a small bonus rewards documents where
    those terms appear close together in the token stream:

        proximity_bonus = PROXIMITY_ALPHA / (1 + min_distance)

    where min_distance is the smallest gap (in token positions) between any
    two query terms' occurrences in the document.  PROXIMITY_ALPHA is chosen
    so the bonus is always much smaller than the TF-IDF score -- it acts as a
    tiebreaker, not a score override.

    Complexity notes
    ----------------
    - get_word_entry: O(1) average (dictionary lookup)
    - find (single term): O(D) where D = documents containing the term
    - find (multi-term): O(T * D) for AND intersection + ranking, where
      T = number of query terms, D = candidate documents
    - Proximity scoring: O(P^2) in the number of stored positions per document,
      acceptable for the small corpora targeted by this tool
    - suggest_terms: O(V) where V = vocabulary size (scans all indexed words)
    """

    PROXIMITY_ALPHA: float = 0.5  # keeps bonus well below typical TF-IDF scores

    def __init__(self, index: InvertedIndex) -> None:
        self._index = index

    # ------------------------------------------------------------------
    # TF-IDF helpers
    # ------------------------------------------------------------------

    def _total_docs(self) -> int:
        """Return the number of indexed documents."""
        return len(self._index._docs)

    def _idf(self, word: str) -> float:
        """
        Compute smoothed IDF for a word.

        idf = log((1 + N) / (1 + df)) + 1

        The +1 additive smoothing ensures IDF >= 1 for any term, avoiding
        zero scores for very common words such as 'the'.
        """
        n = self._total_docs()
        df = len(self._index.get_word(word))  # number of docs containing word
        return math.log((1 + n) / (1 + df)) + 1

    def _tfidf(self, word: str, url: str) -> float:
        """Return the TF-IDF score for a single word in a single document."""
        entry = self._index.get_word(word)
        if url not in entry:
            return 0.0
        tf = entry[url]["frequency"]
        return tf * self._idf(word)

    # ------------------------------------------------------------------
    # Proximity bonus
    # ------------------------------------------------------------------

    def _proximity_bonus(self, terms: list[str], url: str) -> float:
        """
        Return a small proximity bonus for multi-word queries.

        Finds the minimum token-position distance between any pair of query
        terms in the given document, then computes:

            bonus = PROXIMITY_ALPHA / (1 + min_distance)

        A distance of 1 (adjacent tokens) gives the maximum bonus of
        ALPHA/2 ≈ 0.25.  A distance of 100 gives ≈ 0.005.

        Returns 0.0 for single-term queries or when any term is absent.

        Complexity: O(P^2) in total positions across query terms, which is
        negligible for the small pages on quotes.toscrape.com.
        """
        if len(terms) < 2:
            return 0.0

        all_positions: list[list[int]] = []
        for term in terms:
            entry = self._index.get_word(term)
            if url not in entry:
                return 0.0
            all_positions.append(entry[url]["positions"])

        min_dist = float("inf")
        for i in range(len(all_positions)):
            for j in range(i + 1, len(all_positions)):
                for p1 in all_positions[i]:
                    for p2 in all_positions[j]:
                        dist = abs(p1 - p2)
                        if dist < min_dist:
                            min_dist = dist

        if min_dist == float("inf"):
            return 0.0
        return self.PROXIMITY_ALPHA / (1 + min_dist)

    # ------------------------------------------------------------------
    # Query suggestions
    # ------------------------------------------------------------------

    def suggest_terms(self, term: str) -> list[str]:
        """
        Return up to three close matches for a term not found in the index.

        Uses difflib.get_close_matches against the full vocabulary.
        Complexity: O(V) where V is the number of unique indexed terms.
        Returns an empty list if no close matches exist.
        """
        all_words = list(self._index._index.keys())
        return difflib.get_close_matches(term.lower(), all_words, n=3, cutoff=0.75)

    # ------------------------------------------------------------------
    # Core query methods
    # ------------------------------------------------------------------

    def get_word_entry(self, word: str) -> dict:
        """Return the raw index entry for a single word."""
        return self._index.get_word(word)

    def find(self, query: str) -> list[dict]:
        """
        Return pages containing ALL query terms, ranked by TF-IDF + proximity.

        Result structure::

            {
                "url": "...",
                "score": 12,            # raw frequency sum (kept for compatibility)
                "tfidf_score": 3.45,    # TF-IDF weighted score
                "proximity_bonus": 0.12,# bonus for co-located terms
                "final_score": 3.57,    # tfidf_score + proximity_bonus (ranking key)
                "matched_terms": ["good", "friends"],
                "frequencies": {"good": 3, "friends": 2}
            }

        Multi-word queries require ALL terms to be present (AND logic).
        Results are sorted by final_score descending.

        Complexity: O(T * D) for intersection and ranking, plus O(P^2) per
        candidate document for proximity scoring.
        """
        terms = normalise_query(query)
        if not terms:
            return []

        # Collect per-term posting entries -- O(T)
        term_entries: dict[str, dict] = {t: self._index.get_word(t) for t in terms}

        # AND intersection: candidates must appear in every term's posting list
        candidate_urls: set[str] | None = None
        for entry in term_entries.values():
            urls = set(entry.keys())
            candidate_urls = urls if candidate_urls is None else candidate_urls & urls

        if not candidate_urls:
            return []

        results: list[dict] = []
        for url in candidate_urls:
            frequencies = {t: term_entries[t][url]["frequency"] for t in terms}
            tfidf = sum(self._tfidf(t, url) for t in terms)
            prox = self._proximity_bonus(terms, url)
            results.append(
                {
                    "url": url,
                    "score": sum(frequencies.values()),      # raw sum, backward compat
                    "tfidf_score": round(tfidf, 4),
                    "proximity_bonus": round(prox, 4),
                    "final_score": round(tfidf + prox, 4),
                    "matched_terms": terms,
                    "frequencies": frequencies,
                }
            )

        results.sort(key=lambda r: r["final_score"], reverse=True)
        return results

    # ------------------------------------------------------------------
    # Formatting helpers
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
        """
        Return a human-readable summary of find results.

        If no results are found and one or more query terms are missing from
        the index, close-match suggestions are appended automatically.
        """
        terms = normalise_query(query)
        if not terms:
            return "Please provide at least one search term."

        results = self.find(query)
        if not results:
            lines = [f'No pages found containing all of: {", ".join(terms)}.']
            # Suggest corrections for any term not present in the index
            for term in terms:
                if not self._index.get_word(term):
                    suggestions = self.suggest_terms(term)
                    if suggestions:
                        lines.append(
                            f'  Did you mean "{suggestions[0]}" instead of "{term}"?'
                        )
            return "\n".join(lines)

        lines = [
            f"Found {len(results)} page(s) for query: {', '.join(terms)}",
            "",
        ]
        for rank, result in enumerate(results, start=1):
            lines.append(f"  {rank}. {result['url']}")
            lines.append(f"     tfidf score    : {result['tfidf_score']}")
            lines.append(f"     proximity bonus: {result['proximity_bonus']}")
            lines.append(f"     final score    : {result['final_score']}")
            for term, freq in result["frequencies"].items():
                lines.append(f"     {term!r:12s}: {freq} occurrence(s)")
        return "\n".join(lines)
