"""Entry point — parses CLI arguments and dispatches to the correct command."""

import sys


USAGE = """
COMP3011 Search Engine Tool
============================
Usage:
  python -m src.main build               Crawl the website and build the index
  python -m src.main load                Load an existing index from disk
  python -m src.main print <word>        Show frequency info for a word
  python -m src.main find <query ...>    Search the index for matching pages
"""


def main(args: list[str] | None = None) -> None:
    if args is None:
        args = sys.argv[1:]

    if not args:
        print(USAGE)
        return

    command = args[0].lower()

    if command == "build":
        print("build: not yet implemented")
    elif command == "load":
        print("load: not yet implemented")
    elif command == "print":
        print("print: not yet implemented")
    elif command == "find":
        print("find: not yet implemented")
    else:
        print(f"Unknown command: {command!r}")
        print(USAGE)


if __name__ == "__main__":
    main()
