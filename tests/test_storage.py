"""Tests for save_index, load_index, and index_exists."""

import json

import pytest

from src.storage import index_exists, load_index, save_index

SAMPLE_INDEX = {
    "index": {
        "hello": {
            "https://example.com/": {"frequency": 2, "positions": [0, 5]}
        }
    },
    "docs": {
        "https://example.com/": {"word_count": 10, "title": "Example"}
    },
}


# ---------------------------------------------------------------------------
# save_index
# ---------------------------------------------------------------------------

def test_save_creates_file(tmp_path):
    dest = tmp_path / "index.json"
    save_index(SAMPLE_INDEX, dest)
    assert dest.exists()


def test_save_writes_valid_json(tmp_path):
    dest = tmp_path / "index.json"
    save_index(SAMPLE_INDEX, dest)
    loaded = json.loads(dest.read_text(encoding="utf-8"))
    assert loaded == SAMPLE_INDEX


def test_save_json_is_indented(tmp_path):
    dest = tmp_path / "index.json"
    save_index(SAMPLE_INDEX, dest)
    raw = dest.read_text(encoding="utf-8")
    # Indented JSON has newlines
    assert "\n" in raw


def test_save_creates_parent_directories(tmp_path):
    dest = tmp_path / "nested" / "deep" / "index.json"
    save_index(SAMPLE_INDEX, dest)
    assert dest.exists()


# ---------------------------------------------------------------------------
# load_index
# ---------------------------------------------------------------------------

def test_load_returns_correct_data(tmp_path):
    dest = tmp_path / "index.json"
    save_index(SAMPLE_INDEX, dest)
    result = load_index(dest)
    assert result == SAMPLE_INDEX


def test_load_round_trip_preserves_structure(tmp_path):
    dest = tmp_path / "index.json"
    save_index(SAMPLE_INDEX, dest)
    result = load_index(dest)
    assert result["index"]["hello"]["https://example.com/"]["frequency"] == 2
    assert result["docs"]["https://example.com/"]["title"] == "Example"


def test_load_missing_file_raises_file_not_found(tmp_path):
    missing = tmp_path / "does_not_exist.json"
    with pytest.raises(FileNotFoundError):
        load_index(missing)


def test_load_corrupt_json_raises_value_error(tmp_path):
    dest = tmp_path / "index.json"
    dest.write_text("{ this is not valid json !!!", encoding="utf-8")
    with pytest.raises(ValueError):
        load_index(dest)


# ---------------------------------------------------------------------------
# index_exists
# ---------------------------------------------------------------------------

def test_index_exists_returns_true_when_file_present(tmp_path):
    dest = tmp_path / "index.json"
    save_index(SAMPLE_INDEX, dest)
    assert index_exists(dest) is True


def test_index_exists_returns_false_when_missing(tmp_path):
    missing = tmp_path / "does_not_exist.json"
    assert index_exists(missing) is False
