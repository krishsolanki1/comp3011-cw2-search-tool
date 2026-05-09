"""Interactive command-line shell — wires crawler, indexer, storage, and search."""

import sys

from src.crawler import Crawler
from src.indexer import InvertedIndex
from src.search import SearchEngine
from src.storage import INDEX_PATH, index_exists, load_index, save_index

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
  find <query ...>   Search for pages matching all query terms
  stats              Show summary statistics for the loaded index
  help               Show this help message
  exit / quit        Exit the shell
"""

BASE_URL = "https://quotes.toscrape.com/"


def _build(engine_ref: list) -> None:
    print(f"Starting crawl of {BASE_URL} (delay=6s between pages)…")
    crawler = Crawler(base_url=BASE_URL, delay_seconds=6)
    pages = crawler.crawl()

    if not pages:
        print("Crawl returned no pages. Check your network connection.")
        return

    print(f"Crawled {len(pages)} page(s). Building index…")
    idx = InvertedIndex()
    idx.build_from_pages(pages)

    data = idx.to_dict()
    save_index(data, INDEX_PATH)
    print(f"Index saved to {INDEX_PATH}.")
    print(f"Unique terms: {len(data['index'])}  |  Pages indexed: {len(data['docs'])}")

    engine_ref[0] = SearchEngine(idx)
    print("Index is ready — you can now use 'print' and 'find'.")


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
    if not engine:
        print("No index loaded. Run 'build' or 'load' first.")
        return
    data = engine._index.to_dict()
    print(f"Pages indexed : {len(data['docs'])}")
    print(f"Unique terms  : {len(data['index'])}")
    print(f"Index path    : {INDEX_PATH}")


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
        else:
            print(f"Unknown command: {command!r}. Type 'help' for options.")


def main(args: list[str] | None = None) -> None:
    """Entry point — run as interactive shell (default) or one-shot command."""
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
    else:
        print(f"Unknown command: {command!r}")
        print("Run without arguments to open the interactive shell.")


if __name__ == "__main__":
    main()
