"""Interactive command-line shell -- wires crawler, indexer, and search."""

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from src.crawler import Crawler
from src.indexer import InvertedIndex
from src.search import SearchEngine

# ---------------------------------------------------------------------------
# Storage helpers (index persistence)
# ---------------------------------------------------------------------------

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

BANNER = """
============================================================
  COMP3011 Search Engine Tool
  Target: https://quotes.toscrape.com/
============================================================
Type 'help' for available commands.
"""

HELP_TEXT = """
Commands:
  build              Crawl the website, build the index, and save it
  load               Load a previously saved index from disk
  print <word>       Show the index entry for a word
  find <query ...>   Search for pages matching all query terms (TF-IDF ranked)
  stats              Show detailed index statistics and top terms
  benchmark          Time sample queries against the loaded index
  help               Show this help message
  exit / quit        Exit the shell
"""

BASE_URL = "https://quotes.toscrape.com/"

# Sample queries used by the benchmark command
_BENCHMARK_QUERIES = ["love", "good", "life", "the", "truth", "world"]


def _build(engine_ref: list) -> None:
    print(f"Starting crawl of {BASE_URL} (delay=6s between pages)...")
    crawler = Crawler(base_url=BASE_URL, delay_seconds=6)
    pages = crawler.crawl()

    if not pages:
        print("Crawl returned no pages. Check your network connection.")
        return

    print(f"Crawled {len(pages)} page(s). Building index...")
    idx = InvertedIndex()
    idx.build_from_pages(pages)
    idx.built_at = datetime.now(timezone.utc).isoformat()

    data = idx.to_dict()
    save_index(data, INDEX_PATH)
    print(f"Index saved to {INDEX_PATH}.")
    print(f"Unique terms: {len(data['index'])}  |  Pages indexed: {len(data['docs'])}")

    engine_ref[0] = SearchEngine(idx)
    print("Index is ready -- you can now use 'print' and 'find'.")


def _load(engine_ref: list) -> None:
    if not index_exists(INDEX_PATH):
        print(f"No index file found at {INDEX_PATH}. Run 'build' first.")
        return

    data = load_index(INDEX_PATH)
    idx = InvertedIndex.from_dict(data)
    engine_ref[0] = SearchEngine(idx)
    print(f"Index loaded from {INDEX_PATH}.")
    print(f"Unique terms: {len(data['index'])}  |  Pages indexed: {len(data['docs'])}")


def _print_word(engine: SearchEngine | None, word: str) -> None:
    if not engine:
        print("No index loaded. Run 'build' or 'load' first.")
        return
    print(engine.format_word_entry(word))


def _find(engine: SearchEngine | None, query: str) -> None:
    if not engine:
        print("No index loaded. Run 'build' or 'load' first.")
        return
    print(engine.format_find_results(query))


def _stats(engine: SearchEngine | None) -> None:
    """
    Display detailed index statistics.

    Computing top terms is O(V log V) in vocabulary size for the sort.
    For a site of this size (hundreds to low thousands of terms) this is instant.
    """
    if not engine:
        print("No index loaded. Run 'build' or 'load' first.")
        return

    idx = engine._index
    total_docs = len(idx._docs)
    total_terms = len(idx._index)
    total_postings = sum(len(urls) for urls in idx._index.values())

    # Top 10 terms ranked by total corpus frequency
    term_totals = {
        word: sum(v["frequency"] for v in urls.values())
        for word, urls in idx._index.items()
    }
    top_terms = sorted(term_totals.items(), key=lambda x: x[1], reverse=True)[:10]

    print(f"Pages indexed  : {total_docs}")
    print(f"Unique terms   : {total_terms}")
    print(f"Total postings : {total_postings}")
    print(f"Index path     : {INDEX_PATH}")
    if idx.built_at:
        print(f"Built at       : {idx.built_at}")
    print()
    print("Top 10 terms by corpus frequency:")
    for i, (word, total) in enumerate(top_terms, 1):
        print(f"  {i:2}. {word:<20s} {total}")


def _benchmark(engine: SearchEngine | None) -> None:
    """
    Run local timing measurements against the loaded index.

    Does NOT make any network requests. Runs each sample query 1000 times
    to produce a stable average.  This gives evidence of index lookup speed
    and is useful for explaining algorithm complexity in the video.
    """
    if not engine:
        print("No index loaded. Run 'build' or 'load' first.")
        return

    idx = engine._index
    total_docs = len(idx._docs)
    total_terms = len(idx._index)
    total_postings = sum(len(urls) for urls in idx._index.values())
    avg_postings = total_postings / total_terms if total_terms else 0.0

    # Only benchmark queries whose terms are actually in the index
    queries = [
        q for q in _BENCHMARK_QUERIES
        if all(idx.get_word(t) for t in q.split())
    ]
    if not queries:
        # Fall back to the first two indexed terms
        queries = list(idx._index.keys())[:2]

    print("Index benchmark")
    print(f"  Documents         : {total_docs}")
    print(f"  Unique terms      : {total_terms}")
    print(f"  Total postings    : {total_postings}")
    print(f"  Avg postings/term : {avg_postings:.1f}")
    print()
    print("  Query timing (1000 repetitions each):")
    for query in queries[:4]:
        start = time.perf_counter()
        for _ in range(1000):
            engine.find(query)
        elapsed_ms = (time.perf_counter() - start) * 1000
        print(
            f"    {query!r:<20s}: {elapsed_ms:6.1f} ms total"
            f"  /  {elapsed_ms / 1000:.3f} ms avg"
        )


def run_shell() -> None:
    """Start the interactive command loop."""
    print(BANNER)
    engine_ref: list[SearchEngine | None] = [None]

    while True:
        try:
            raw = input(">> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not raw:
            continue

        parts = raw.split()
        command = parts[0].lower()

        if command in ("exit", "quit"):
            print("Goodbye.")
            break
        elif command == "help":
            print(HELP_TEXT)
        elif command == "build":
            _build(engine_ref)
        elif command == "load":
            _load(engine_ref)
        elif command == "print":
            if len(parts) < 2:
                print("Usage: print <word>")
            else:
                _print_word(engine_ref[0], parts[1])
        elif command == "find":
            if len(parts) < 2:
                print("Usage: find <query terms>")
            else:
                _find(engine_ref[0], " ".join(parts[1:]))
        elif command == "stats":
            _stats(engine_ref[0])
        elif command == "benchmark":
            _benchmark(engine_ref[0])
        else:
            print(f"Unknown command: {command!r}. Type 'help' for options.")


def main(args: list[str] | None = None) -> None:
    """Entry point -- run as interactive shell (default) or one-shot command."""
    if args is None:
        args = sys.argv[1:]

    if not args:
        run_shell()
        return

    # Allow one-shot usage: python -m src.main find good
    engine_ref: list[SearchEngine | None] = [None]
    command = args[0].lower()

    if command == "build":
        _build(engine_ref)
    elif command == "load":
        _load(engine_ref)
    elif command == "print":
        _load(engine_ref)
        if len(args) < 2:
            print("Usage: python -m src.main print <word>")
        else:
            _print_word(engine_ref[0], args[1])
    elif command == "find":
        _load(engine_ref)
        if len(args) < 2:
            print("Usage: python -m src.main find <query terms>")
        else:
            _find(engine_ref[0], " ".join(args[1:]))
    elif command == "stats":
        _load(engine_ref)
        _stats(engine_ref[0])
    elif command == "benchmark":
        _load(engine_ref)
        _benchmark(engine_ref[0])
    else:
        print(f"Unknown command: {command!r}")
        print("Run without arguments to open the interactive shell.")


if __name__ == "__main__":
    main()
