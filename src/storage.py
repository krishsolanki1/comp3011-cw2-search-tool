"""Storage — saves and loads the inverted index as a JSON file."""

import json
from pathlib import Path

INDEX_PATH = Path("data/index.json")


def save_index(index_data: dict, path: str | Path = INDEX_PATH) -> None:
    """Write index_data to a JSON file, creating parent directories as needed."""
    dest = Path(path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(index_data, indent=2), encoding="utf-8")


def load_index(path: str | Path = INDEX_PATH) -> dict:
    """Read and return the index from a JSON file.

    Raises FileNotFoundError if the file does not exist.
    Raises ValueError if the file contains invalid JSON.
    """
    src = Path(path)
    if not src.exists():
        raise FileNotFoundError(f"Index file not found: {src}")
    try:
        return json.loads(src.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Index file contains invalid JSON: {src}") from exc


def index_exists(path: str | Path = INDEX_PATH) -> bool:
    """Return True if the index file exists at the given path."""
    return Path(path).exists()
