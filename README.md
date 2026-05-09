# COMP3011 Coursework 2 -- Search Engine Tool

**Module:** COMP3011 Web Services and Web Data
**Student:** Krish Solanki
**University:** University of Nottingham
**Academic Year:** 2025-2026

---

## Overview

This is a command-line search engine tool that crawls the website [https://quotes.toscrape.com/](https://quotes.toscrape.com/), builds an inverted index from the scraped page content, persists the index to disk, and supports word-frequency lookups and multi-term ranked search queries.

The tool is built entirely in Python using `requests` for HTTP, `BeautifulSoup` for HTML parsing, and the Python standard library for everything else.

---

## Features

- Polite web crawler with a configurable delay between requests (default: 6 seconds)
- Inverted index storing per-document word frequency and token positions
- Case-insensitive tokenisation
- Single-word lookup: frequency and position data
- Multi-word search with AND logic and combined-frequency ranking
- JSON persistence to `data/index.json`
- Interactive command-line shell
- 95 unit tests with 98% line coverage

---

## Coursework Requirements Covered

| Requirement | Implementation |
|---|---|
| Crawl the target website | `src/crawler.py` -- follows pagination via `li.next > a` links |
| Build an inverted index | `src/indexer.py` -- word frequency and positions per URL |
| `build` command | Crawls, indexes, and saves to `data/index.json` |
| `load` command | Loads `data/index.json` and initialises the search engine |
| `print <word>` command | Displays frequency and positions for a word |
| `find <query terms>` command | Returns ranked pages matching all query terms |
| Politeness | 6-second sleep between successive page fetches |
| Error handling | Network failures print a message and stop gracefully |
| Testing | `pytest` with `pytest-cov`, 98% line coverage |

---

## Project Structure

```
comp3011-cw2-search-tool/
├── src/
│   ├── __init__.py
│   ├── crawler.py      # Web crawler -- follows pagination, respects politeness delay
│   ├── indexer.py      # Text extraction, tokenisation, inverted index builder
│   ├── search.py       # Query normalisation, ranked search, output formatting
│   ├── storage.py      # JSON save/load/exists helpers
│   └── main.py         # Interactive CLI shell and one-shot entry point
├── tests/
│   ├── test_crawler.py   # 10 tests
│   ├── test_indexer.py   # 18 tests
│   ├── test_search.py    # 22 tests
│   ├── test_storage.py   # 10 tests
│   └── test_main.py      # 35 tests (includes integration test)
├── data/
│   └── index.json        # Generated at runtime by `build` -- required for submission
├── requirements.txt
└── README.md
```

---

## Installation

**Requirements:** Python 3.9 or higher.

```bash
# Clone the repository
git clone https://github.com/krishsolanki1/comp3011-cw2-search-tool.git
cd comp3011-cw2-search-tool

# Install dependencies
pip install -r requirements.txt
```

**Dependencies** (`requirements.txt`):

| Package | Purpose |
|---|---|
| `requests` | HTTP requests for the crawler |
| `beautifulsoup4` | HTML parsing for text extraction |
| `pytest` | Test runner |
| `pytest-cov` | Coverage reporting |

### Quick verification scripts

Two scripts are provided to set up a virtual environment, install dependencies, and run the test suite in one step.

**Linux / macOS:**

```bash
bash verify.sh
```

**Windows PowerShell:**

```powershell
.\verify.ps1
```

---

## Running the Tool

### Interactive shell (recommended for the video)

```bash
python -m src.main
```

This opens an interactive prompt:

```
============================================================
  COMP3011 Search Engine Tool
  Target: https://quotes.toscrape.com/
============================================================
Type 'help' for available commands.

>>
```

### Available shell commands

| Command | Description |
|---|---|
| `build` | Crawl the website, build the index, save to `data/index.json` |
| `load` | Load a previously saved index from `data/index.json` |
| `print <word>` | Show frequency and positions for a single word |
| `find <query terms>` | Search for pages matching all query terms |
| `stats` | Show index summary (pages, terms, path) |
| `help` | Show command list |
| `exit` / `quit` | Exit the shell |

---

## Command Examples

### `build`

Crawls all pages of the target site, builds the inverted index, and saves it.
The 6-second politeness delay is applied between each page fetch.

```
>> build
Starting crawl of https://quotes.toscrape.com/ (delay=6s between pages)...
Crawled 11 page(s). Building index...
Index saved to data/index.json.
Unique terms: 843  |  Pages indexed: 11
Index is ready -- you can now use 'print' and 'find'.
```

### `load`

Loads the saved index from `data/index.json` without re-crawling.

```
>> load
Index loaded from data/index.json.
Unique terms: 843  |  Pages indexed: 11
```

### `print <word>`

Displays the inverted index entry for a single word, including which pages it
appears on, how many times, and at which token positions.

```
>> print indifference
Word: "indifference"
  Found on 1 page(s):
    https://quotes.toscrape.com/
      frequency : 1
      positions : [42]
```

If the word is not in the index:

```
>> print nonsense
No index entry found for "nonsense".
```

### `find <query terms>`

Returns all pages that contain every query term, ranked by combined frequency.
Search is case-insensitive.

```
>> find indifference
Found 1 page(s) for query: indifference

  1. https://quotes.toscrape.com/
     score : 1
     'indifference': 1 occurrence(s)
```

```
>> find good friends
Found 1 page(s) for query: good, friends

  1. https://quotes.toscrape.com/page/4/
     score : 3
     'good'   : 2 occurrence(s)
     'friends': 1 occurrence(s)
```

If no pages match all terms:

```
>> find good friends zzznonsense
No pages found containing all of: good, friends, zzznonsense.
```

### `stats`

```
>> stats
Pages indexed : 11
Unique terms  : 843
Index path    : data/index.json
```

### One-shot usage (without the interactive shell)

Commands can also be run directly from the terminal:

```bash
python -m src.main build
python -m src.main load
python -m src.main print indifference
python -m src.main find good friends
```

---

## Inverted Index Design

### Structure

The index is a nested dictionary mapping each word to a per-URL entry:

```json
{
  "index": {
    "indifference": {
      "https://quotes.toscrape.com/": {
        "frequency": 1,
        "positions": [42]
      }
    }
  },
  "docs": {
    "https://quotes.toscrape.com/": {
      "word_count": 312,
      "title": "Quotes to Scrape"
    }
  }
}
```

### Tokenisation

Text is extracted using BeautifulSoup with `<script>`, `<style>`, `<head>`, and `<noscript>` tags removed. The remaining text is lowercased and split using the regular expression `[a-z0-9]+`, which removes all punctuation and retains only alphanumeric tokens.

This means "Good", "GOOD", and "good" are treated identically, satisfying the case-insensitive requirement.

### Lookup complexity

A single-word lookup (`get_word`) is an O(1) dictionary lookup. Position data is stored as a list so it can be reported directly without reprocessing.

---

## Crawling and Politeness Policy

The `Crawler` class (`src/crawler.py`) works as follows:

1. Fetches the base URL using a `requests.Session` with a descriptive `User-Agent` header.
2. Parses the HTML with BeautifulSoup and extracts the `li.next > a` link.
3. Converts relative next-page URLs to absolute using `urllib.parse.urljoin`.
4. Before fetching the next page, sleeps for `delay_seconds` (default: 6 seconds).
5. Stops when there is no next link, a URL has already been visited, or a request fails.

**Domain restriction:** The crawler checks that any discovered next link belongs to the same domain as the base URL. External links are silently ignored.

**Error handling:** Any `requests.RequestException` (connection error, timeout, HTTP error) is caught, a message is printed, and the crawl stops cleanly without raising an exception to the caller.

---

## Search and Ranking

### Single-word query

`print <word>` uses `get_word_entry` to retrieve the raw index entry and format it with per-URL frequency and position data.

### Multi-word query (`find`)

`find <query>` normalises the query using the same tokeniser as the indexer, then:

1. Retrieves the index entry for each term.
2. Computes the intersection of URLs that appear in every term's entry (AND logic).
3. For each candidate URL, calculates a score equal to the sum of frequencies across all matched terms.
4. Returns results sorted by score in descending order.

A page must contain all query terms to appear in results. This avoids irrelevant partial matches.

### Result format

Each result includes the URL, total score, matched terms, and per-term frequency breakdown, making it straightforward to explain during the demonstration video.

---

## Testing

### Running the tests

```bash
# Run all tests
pytest

# Run with line-by-line coverage report
pytest --cov=src --cov-report=term-missing
```

### Coverage summary

| Module | Coverage |
|---|---|
| `src/crawler.py` | 98% |
| `src/indexer.py` | 100% |
| `src/search.py` | 100% |
| `src/storage.py` | 100% |
| `src/main.py` | 96% |
| **Total** | **98%** |

### What the tests cover

- **Crawler:** follows next links, collects multiple pages, avoids duplicates, calls the sleeper between requests, handles `RequestException` gracefully, ignores external-domain links, sets a User-Agent header.
- **Indexer:** excludes `<script>`/`<style>` content, lowercases and strips punctuation, records correct frequencies and positions, handles multiple documents, round-trip serialisation.
- **Search:** single-word and multi-word queries, case-insensitive matching, AND intersection logic, frequency-based ranking, empty and missing queries, output formatting.
- **Storage:** creates files and parent directories, writes indented JSON, raises `FileNotFoundError` for missing files, raises `ValueError` for corrupt JSON.
- **Main:** all CLI helper functions, interactive shell commands (help, build, load, print, find, stats, exit, unknown input, empty input, EOF), one-shot command dispatch.
- **Integration:** a complete fake-crawl-to-search pipeline using in-memory HTML pages, covering index building, search, ranking, and round-trip JSON serialisation.

All unit tests use mocked HTTP sessions and patched sleep functions. No test contacts the live website or waits any real time.

---

## GenAI Usage Declaration

This project was developed with the assistance of Claude (Anthropic), an AI assistant, acting as a pair-programming tool throughout the development process.

**How AI was used:**

- Generating initial file scaffolding and class skeletons based on described requirements.
- Suggesting implementations for the crawler pagination logic, tokenisation regex, and inverted index structure.
- Writing test scaffolding and suggesting edge cases to cover.
- Reviewing code for clarity, typing, and consistency.
- Assisting with README structure and wording.

**Student responsibility:**

All AI-generated code and suggestions were reviewed, tested, and understood before being accepted. The student directed the design decisions, verified correctness against the coursework specification, ran all tests, and can explain every part of the codebase. The AI acted as a tool; the understanding and judgement are the student's own.

This declaration is made honestly in accordance with the COMP3011 academic integrity guidelines.

---

## Limitations and Future Improvements

- **Tokenisation:** the current `[a-z0-9]+` regex discards punctuation entirely. A more sophisticated tokeniser could handle hyphenated words or apostrophes.
- **Ranking:** results are ranked by raw combined term frequency. A TF-IDF or BM25 scoring model would give more meaningful rankings on larger corpora.
- **Crawl scope:** the crawler only follows `li.next` pagination links. Internal links to individual quote pages or author pages are not followed.
- **No stemming:** "run", "running", and "runs" are treated as distinct terms. A stemmer (e.g. Porter Stemmer) would improve recall.
- **Single-threaded:** the crawler fetches one page at a time. Asynchronous fetching (e.g. `aiohttp`) would be faster, though politeness constraints already limit throughput.

---

## Submission Notes

- The `data/index.json` file is generated by running `build` and is required for submission. It is not gitignored.
- The GitHub repository URL is: [https://github.com/krishsolanki1/comp3011-cw2-search-tool](https://github.com/krishsolanki1/comp3011-cw2-search-tool)
- The video demonstration link will be provided separately on the submission form.
- To reproduce the index from scratch, run `python -m src.main build` from the project root with an internet connection.
