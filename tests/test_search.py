"""Tests for normalise_query and SearchEngine."""

import pytest

from src.indexer import InvertedIndex
from src.search import SearchEngine, normalise_query

# ---------------------------------------------------------------------------
# Shared index fixture
# ---------------------------------------------------------------------------

PAGE1 = "<html><body><p>good good bad</p></body></html>"
PAGE2 = "<html><body><p>bad bad bad good friends</p></body></html>"
PAGE3 = "<html><body><p>friends only</p></body></html>"


@pytest.fixture()
def engine() -> SearchEngine:
    idx = InvertedIndex()
    idx.add_document("https://example.com/page1/", PAGE1)
    idx.add_document("https://example.com/page2/", PAGE2)
    idx.add_document("https://example.com/page3/", PAGE3)
    return SearchEngine(idx)


# ---------------------------------------------------------------------------
# normalise_query
# ---------------------------------------------------------------------------

def test_normalise_query_lowercases():
    assert normalise_query("Good WORLD") == ["good", "world"]


def test_normalise_query_strips_punctuation():
    assert normalise_query("hello, world!") == ["hello", "world"]


def test_normalise_query_empty_string():
    assert normalise_query("") == []


def test_normalise_query_whitespace_only():
    assert normalise_query("   ") == []


# ---------------------------------------------------------------------------
# get_word_entry
# ---------------------------------------------------------------------------

def test_get_word_entry_known_word(engine):
    entry = engine.get_word_entry("good")
    assert "https://example.com/page1/" in entry
    assert "https://example.com/page2/" in entry


def test_get_word_entry_missing_word(engine):
    assert engine.get_word_entry("zzznonsense") == {}


# ---------------------------------------------------------------------------
# find — single-word query
# ---------------------------------------------------------------------------

def test_find_single_word_returns_matching_pages(engine):
    results = engine.find("friends")
    urls = {r["url"] for r in results}
    assert "https://example.com/page2/" in urls
    assert "https://example.com/page3/" in urls


def test_find_single_word_excludes_non_matching(engine):
    results = engine.find("friends")
    urls = {r["url"] for r in results}
    assert "https://example.com/page1/" not in urls


def test_find_missing_word_returns_empty(engine):
    assert engine.find("zzznonsense") == []


def test_find_empty_query_returns_empty(engine):
    assert engine.find("") == []


# ---------------------------------------------------------------------------
# find — case-insensitive
# ---------------------------------------------------------------------------

def test_find_is_case_insensitive(engine):
    lower = engine.find("good")
    upper = engine.find("GOOD")
    mixed = engine.find("Good")
    assert {r["url"] for r in lower} == {r["url"] for r in upper}
    assert {r["url"] for r in lower} == {r["url"] for r in mixed}


# ---------------------------------------------------------------------------
# find — multi-word query (AND logic)
# ---------------------------------------------------------------------------

def test_find_multi_word_and_logic(engine):
    # "good" AND "friends" — only page2 has both
    results = engine.find("good friends")
    urls = {r["url"] for r in results}
    assert urls == {"https://example.com/page2/"}


def test_find_multi_word_excludes_partial_match(engine):
    # page1 has "good" but not "friends"
    results = engine.find("good friends")
    urls = {r["url"] for r in results}
    assert "https://example.com/page1/" not in urls


# ---------------------------------------------------------------------------
# find — ranking by combined frequency
# ---------------------------------------------------------------------------

def test_find_results_ranked_by_score(engine):
    # page2 has bad×3, page1 has bad×1 → page2 should rank first
    results = engine.find("bad")
    assert results[0]["url"] == "https://example.com/page2/"


def test_find_result_score_equals_sum_of_frequencies(engine):
    results = engine.find("good friends")
    assert len(results) == 1
    r = results[0]
    assert r["score"] == r["frequencies"]["good"] + r["frequencies"]["friends"]


def test_find_result_contains_matched_terms(engine):
    results = engine.find("good friends")
    assert results[0]["matched_terms"] == ["good", "friends"]


# ---------------------------------------------------------------------------
# format_word_entry
# ---------------------------------------------------------------------------

def test_format_word_entry_contains_word(engine):
    output = engine.format_word_entry("good")
    assert "good" in output


def test_format_word_entry_contains_frequency(engine):
    output = engine.format_word_entry("good")
    assert "frequency" in output


def test_format_word_entry_missing_word(engine):
    output = engine.format_word_entry("zzznonsense")
    assert "No index entry" in output


# ---------------------------------------------------------------------------
# format_find_results
# ---------------------------------------------------------------------------

def test_format_find_results_contains_url(engine):
    output = engine.format_find_results("good")
    assert "https://example.com/" in output


def test_format_find_results_no_results(engine):
    output = engine.format_find_results("zzznonsense")
    assert "No pages found" in output


def test_format_find_results_empty_query(engine):
    output = engine.format_find_results("")
    assert "at least one" in output


# ---------------------------------------------------------------------------
# TF-IDF ranking
# ---------------------------------------------------------------------------

def test_find_result_has_tfidf_score(engine):
    """Each result must include tfidf_score, proximity_bonus, and final_score."""
    results = engine.find("good")
    assert len(results) > 0
    r = results[0]
    assert "tfidf_score" in r
    assert "proximity_bonus" in r
    assert "final_score" in r


def test_find_tfidf_score_positive(engine):
    """TF-IDF score must be strictly positive for any matched document."""
    results = engine.find("good")
    assert all(r["tfidf_score"] > 0 for r in results)


def test_find_final_score_equals_tfidf_plus_proximity(engine):
    """final_score should equal tfidf_score + proximity_bonus (within rounding)."""
    results = engine.find("good friends")
    assert len(results) > 0
    for r in results:
        assert abs(r["final_score"] - (r["tfidf_score"] + r["proximity_bonus"])) < 1e-6


def test_find_tfidf_ranks_higher_frequency_page_first():
    """
    A page with higher term frequency should rank above a page with lower
    frequency when both contain the same term (same IDF).
    """
    high_html = "<html><body><p>apple apple apple apple</p></body></html>"
    low_html = "<html><body><p>apple</p></body></html>"

    idx = InvertedIndex()
    idx.add_document("https://example.com/high/", high_html)
    idx.add_document("https://example.com/low/", low_html)
    engine = SearchEngine(idx)

    results = engine.find("apple")
    assert results[0]["url"] == "https://example.com/high/"


def test_find_tfidf_rare_term_scores_higher_per_occurrence():
    """
    IDF rewards rare terms. A term appearing in fewer documents gets a
    higher IDF weight, so equal TF produces a higher TF-IDF score.
    """
    # "rare" appears in 1 of 3 docs; "common" appears in 3 of 3
    html_a = "<html><body><p>common rare</p></body></html>"
    html_b = "<html><body><p>common</p></body></html>"
    html_c = "<html><body><p>common</p></body></html>"

    idx = InvertedIndex()
    idx.add_document("https://example.com/a/", html_a)
    idx.add_document("https://example.com/b/", html_b)
    idx.add_document("https://example.com/c/", html_c)
    engine = SearchEngine(idx)

    # Both "common" and "rare" appear once in doc a
    # IDF("rare") > IDF("common") because rare is in fewer docs
    tfidf_rare = engine._tfidf("rare", "https://example.com/a/")
    tfidf_common = engine._tfidf("common", "https://example.com/a/")
    assert tfidf_rare > tfidf_common


def test_find_single_term_proximity_bonus_is_zero(engine):
    """Single-term queries must have proximity_bonus == 0."""
    results = engine.find("good")
    assert all(r["proximity_bonus"] == 0.0 for r in results)


def test_tfidf_returns_zero_for_url_not_in_posting():
    """_tfidf defensive guard: returns 0.0 when the URL is not in the term's entry."""
    idx = InvertedIndex()
    idx.add_document("https://example.com/", "<html><body><p>hello</p></body></html>")
    engine = SearchEngine(idx)
    # "hello" exists but "https://other.com/" is not in its posting list
    assert engine._tfidf("hello", "https://other.com/") == 0.0


# ---------------------------------------------------------------------------
# Proximity bonus
# ---------------------------------------------------------------------------

def test_proximity_bonus_positive_for_multi_term(engine):
    """Multi-word queries where terms appear close together give bonus > 0."""
    # PAGE1 = "good good bad" -- good at [0,1], bad at [2], distance = 1
    results = engine.find("good bad")
    assert len(results) > 0
    assert any(r["proximity_bonus"] > 0 for r in results)


def test_proximity_ranking_close_before_far():
    """
    A document where terms appear adjacent should rank above one where they
    are far apart, when TF-IDF scores are equal.
    """
    close_html = "<html><body><p>apple banana</p></body></html>"
    # 20 filler tokens between apple and banana
    far_html = (
        "<html><body><p>apple "
        + " ".join(["filler"] * 20)
        + " banana</p></body></html>"
    )

    idx = InvertedIndex()
    idx.add_document("https://example.com/close/", close_html)
    idx.add_document("https://example.com/far/", far_html)
    engine = SearchEngine(idx)

    results = engine.find("apple banana")
    assert len(results) == 2
    assert results[0]["url"] == "https://example.com/close/"
    assert results[0]["proximity_bonus"] > results[1]["proximity_bonus"]


def test_proximity_bonus_zero_when_term_absent():
    """Proximity bonus is 0 when a term has no positions in the document."""
    idx = InvertedIndex()
    idx.add_document("https://example.com/", "<html><body><p>hello</p></body></html>")
    engine = SearchEngine(idx)
    # "world" is not in the index, so _proximity_bonus should return 0
    assert engine._proximity_bonus(["hello", "world"], "https://example.com/") == 0.0


# ---------------------------------------------------------------------------
# Query suggestions
# ---------------------------------------------------------------------------

def test_suggest_terms_returns_close_match():
    """A misspelling close to an indexed word should produce a suggestion."""
    idx = InvertedIndex()
    idx.add_document(
        "https://example.com/",
        "<html><body><p>friend friendship</p></body></html>",
    )
    engine = SearchEngine(idx)
    suggestions = engine.suggest_terms("frend")
    assert len(suggestions) > 0
    assert any("friend" in s for s in suggestions)


def test_suggest_terms_empty_for_no_match():
    """A completely unrelated term should return no suggestions."""
    idx = InvertedIndex()
    idx.add_document(
        "https://example.com/",
        "<html><body><p>apple banana</p></body></html>",
    )
    engine = SearchEngine(idx)
    assert engine.suggest_terms("xyzzyqqqq") == []


def test_format_find_results_includes_suggestion_for_typo():
    """
    When a query term is absent but a close match exists, the output should
    include a 'Did you mean' hint.
    """
    idx = InvertedIndex()
    idx.add_document(
        "https://example.com/",
        "<html><body><p>friend friendship</p></body></html>",
    )
    engine = SearchEngine(idx)
    output = engine.format_find_results("frend")
    assert "Did you mean" in output


def test_format_find_results_no_suggestion_for_gibberish():
    """
    When no close match exists, the output should not contain a misleading
    suggestion -- just the 'No pages found' message.
    """
    idx = InvertedIndex()
    idx.add_document(
        "https://example.com/",
        "<html><body><p>apple banana</p></body></html>",
    )
    engine = SearchEngine(idx)
    output = engine.format_find_results("xyzzyqqqq")
    assert "No pages found" in output
    assert "Did you mean" not in output
