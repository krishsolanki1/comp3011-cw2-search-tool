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
