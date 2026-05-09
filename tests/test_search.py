"""Tests for the Searcher class."""

import pytest
from src.search import Searcher


def test_searcher_instantiation():
    searcher = Searcher(index={})
    assert searcher.index == {}


def test_searcher_find_not_implemented():
    searcher = Searcher(index={})
    with pytest.raises(NotImplementedError):
        searcher.find("test query")


def test_searcher_print_word_not_implemented():
    searcher = Searcher(index={})
    with pytest.raises(NotImplementedError):
        searcher.print_word("test")
