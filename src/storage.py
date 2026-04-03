"""Storage module — saves and loads the index to/from disk as JSON."""

import json
from pathlib import Path

INDEX_PATH = Path("data/index.json")


class Storage:
    """Handles persistence of the inverted index."""

    def save(self, index: dict, path: Path = INDEX_PATH) -> None:
        """Write the index to a JSON file."""
        raise NotImplementedError

    def load(self, path: Path = INDEX_PATH) -> dict:
        """Read the index from a JSON file and return it."""
        raise NotImplementedError
