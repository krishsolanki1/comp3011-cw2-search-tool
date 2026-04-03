"""Tests for the Indexer class."""

import pytest
from src.indexer import Indexer


def test_indexer_instantiation():
    indexer = Indexer()
    assert indexer.index == {}


def test_indexer_get_missing_word():
    indexer = Indexer()
    assert indexer.get("nonexistent") == {}


def test_indexer_build_not_implemented():
    indexer = Indexer()
    with pytest.raises(NotImplementedError):
        indexer.build([])
