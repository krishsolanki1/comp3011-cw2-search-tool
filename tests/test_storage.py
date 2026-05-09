"""Tests for the Storage class."""

import pytest
from src.storage import Storage


def test_storage_instantiation():
    storage = Storage()
    assert isinstance(storage, Storage)


def test_storage_save_not_implemented():
    storage = Storage()
    with pytest.raises(NotImplementedError):
        storage.save({})


def test_storage_load_not_implemented():
    storage = Storage()
    with pytest.raises(NotImplementedError):
        storage.load()
