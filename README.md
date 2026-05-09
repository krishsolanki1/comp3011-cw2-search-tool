# COMP3011 Coursework 2 -- Search Engine Tool

**Module:** COMP3011 Web Services and Web Data
**Student:** Krish Solanki
**University:** University of Leeds
**Academic Year:** 2025-2026

---

## Overview

This is a command-line search engine tool that crawls the website [https://quotes.toscrape.com/](https://quotes.toscrape.com/), builds an inverted index from the scraped page content, persists the index to disk, and supports word-frequency lookups and multi-term ranked search queries.

The tool is built entirely in Python using `requests` for HTTP, `BeautifulSoup` for HTML parsing, and the Python standard library for everything else.

---

## Features

- Polite web crawler with a configurable delay between requests (default: 6 seconds)
- Two-phase crawl: quote listing pages followed by author biography pages
- Inverted index storing per-document word frequency and token positions
- Case-insensitive tokenisation
- Single-word lookup: frequency and position data
- Multi-word search with AND logic and TF-IDF ranked results
- Proximity-aware scoring bonus for co-located query terms
- Query suggestions via `difflib` for misspelled or near-miss terms
- JSON persistence to `data/index.json`
- Interactive command-line shell with `benchmark` and enhanced `stats`
- 121 unit and integration tests with 97% line coverage

---

## Coursework Requirements Covered

| Requirement | Implementation |
|---|---|
| Crawl the target website | `src/crawler.py` -- follows pagination links then author biography links |
| Build an inverted index | `src/indexer.py` -- word frequency and positions per URL |
| `build` command | Crawls all quote and author pages, indexes, and saves to `data/index.json` |
| `load` command | Loads `data/index.json` and initialises the search engine |
| `print <word>` command | Displays frequency and positions for a word |
| `find <query terms>` command | Returns TF-IDF ranked pages matching all query terms |
| Politeness | 6-second sleep between every page fetch |
| Error handling | Network failures print a message and stop gracefully |
| Testing | `pytest` with `pytest-cov`, 97% line coverage |

---

## Project Structure

```
comp3011-cw2-search-tool/
├── src/
│   ├── __init__.py
│   ├── crawler.py      # Web crawler -- pagination + author pages, politeness delay
│   ├── indexer.py      # Text extraction, tokenisation, inverted index builder
│   ├── search.py       # Query normalisation, TF-IDF ranking, output formatting
│   └── main.py         # Interactive CLI shell, storage helpers, one-shot entry point
├── tests/
│   ├── test_crawler.py   # 14 tests
│   ├── test_indexer.py   # 18 tests
│   ├── test_search.py    # 36 tests
│   └── test_main.py      # 53 tests (includes integration test)
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
| `find <query terms>` | Search for pages matching all query terms (TF-IDF ranked) |
| `stats` | Show detailed index statistics and top terms |
| `benchmark` | Time sample queries against the loaded index |
| `help` | Show command list |
| `exit` / `quit` | Exit the shell |

---

## Command Examples

### `build`

Crawls all quote listing pages and author biography pages, builds the inverted
index, and saves it. The 6-second politeness delay is applied between every
fetch. With 10 quote pages and approximately 50 author pages the full crawl
takes around 6 minutes.

```
>> build
Starting crawl of https://quotes.toscrape.com/ (delay=6s between pages)...
Crawled 60 page(s). Building index...
Index saved to data/index.json.
Unique terms: ...  |  Pages indexed: 60
Index is ready -- you can now use 'print' and 'find'.
```

### `load`

Loads the saved index from `data/index.json` without re-crawling.

```
>> load
Index loaded from data/index.json.
Unique terms: ...  |  Pages indexed: 60
```

### `print <word>`

Displays the inverted index entry for a single word, including which pages it
appears on, how many times, and at which token positions.

```
>> print indifference
Word: "indifference"
  Found on 1 page(s):
    https://quotes.toscrape.com/page/2/
      frequency : 5
      positions : [496, 506, 516, 527, 536]
```

If the word is not in the index:

```
>> print xyzzy
No index entry found for "xyzzy".
```

### `find <query terms>`

Returns all pages that contain every query term, ranked by TF-IDF score.
Search is case-insensitive.

```
>> find indifference
Found 1 page(s) for query: indifference

  1. https://quotes.toscrape.com/page/2/
     tfidf score    : 13.5237
     proximity bonus: 0.0
     final score    : 13.5237
     'indifference': 5 occurrence(s)
```

```
>> find good friends
Found 6 page(s) for query: good, friends

  1. https://quotes.toscrape.com/page/2/
     tfidf score    : 13.356
     proximity bonus: 0.25
     final score    : 13.606
     'good'      : 3 occurrence(s)
     'friends'   : 9 occurrence(s)
  ...
```

If no pages match all terms:

```
>> find good friends zzznonsense
No pages found containing all of: good, friends, zzznonsense.
```

If a term is close to something in the index:

```
>> find frend
No pages found containing all of: frend.
  Did you mean "friend" instead of "frend"?
```

### `stats`

```
>> stats
Pages indexed  : 60
Unique terms   : ...
Total postings : ...
Index path     : data/index.json
Built at       : ...

Top 10 terms by corpus frequency:
   1. ...
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
      "https://quotes.toscrape.com/page/2/": {
        "frequency": 5,
        "positions": [496, 506, 516, 527, 536]
      }
    }
  },
  "docs": {
    "https://quotes.toscrape.com/page/2/": {
      "word_count": 892,
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

The `Crawler` class (`src/crawler.py`) operates in two phases:

**Phase 1 -- Quote listing pages:**
1. Fetches the base URL using a `requests.Session` with a descriptive `User-Agent` header.
2. Parses the HTML with BeautifulSoup and extracts the `li.next > a` pagination link.
3. Converts relative URLs to absolute using `urllib.parse.urljoin`.
4. Sleeps for `delay_seconds` (default: 6 seconds) before each subsequent fetch.
5. While following pagination, collects author biography URLs found via `small.author + a` links.
6. Stops when there is no next link, a URL has already been visited, or a request fails.

**Phase 2 -- Author biography pages:**
7. Fetches each unique author page discovered during Phase 1, with the same politeness delay between each.

**Domain restriction:** All discovered links are checked against the base URL's netloc. External links are silently ignored.

**Error handling:** Any `requests.RequestException` (connection error, timeout, HTTP error) is caught, a message is printed, and the crawl stops cleanly without raising an exception to the caller.

---

## Search and Ranking

### Single-word query

`print <word>` uses `get_word_entry` to retrieve the raw index entry and format it with per-URL frequency and position data.

### Multi-word query (`find`)

`find <query>` normalises the query using the same tokeniser as the indexer, then:

1. Retrieves the index entry for each term.
2. Computes the intersection of URLs that appear in every term's entry (AND logic).
3. Scores each candidate URL using TF-IDF and a proximity bonus.
4. Returns results sorted by final score in descending order.

A page must contain all query terms to appear in results. This avoids irrelevant partial matches.

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
| `src/search.py` | 99% |
| `src/main.py` | 95% |
| **Total** | **97%** |

### What the tests cover

- **Crawler:** follows pagination links, follows author biography links, collects multiple pages, deduplicates author URLs across pages, avoids revisiting URLs, calls the sleeper between every fetch, handles `RequestException` gracefully, ignores external-domain links, sets a User-Agent header.
- **Indexer:** excludes `<script>`/`<style>` content, lowercases and strips punctuation, records correct frequencies and positions, handles multiple documents, round-trip serialisation, `built_at` timestamp persistence.
- **Search:** single-word and multi-word queries, case-insensitive matching, AND intersection logic, TF-IDF ranking, IDF advantage for rare terms, proximity bonus (close vs. far terms), single-term zero bonus, query suggestions for typos, no spurious suggestions for gibberish, output formatting.
- **Main:** all CLI helper functions, interactive shell commands (help, build, load, print, find, stats, benchmark, exit, unknown input, empty input, EOF), one-shot dispatch, benchmark output fields, enhanced stats fields.
- **Integration:** a complete fake-crawl-to-search pipeline using in-memory HTML pages, covering index building, TF-IDF search, ranking, and round-trip JSON serialisation.

All unit tests use mocked HTTP sessions and patched sleep functions. No test contacts the live website or waits any real time.

---

## Advanced Search Features

### TF-IDF Ranking

Raw frequency counting treats every word equally regardless of how common it is across the corpus. A word like "the" appearing three times in a document is far less informative than "indifference" appearing once. TF-IDF (Term Frequency -- Inverse Document Frequency) corrects for this.

The formula used:

```
tf(t, doc)   = raw frequency of term t in document doc
idf(t)       = log( (1 + N) / (1 + df(t)) ) + 1
tfidf(t,doc) = tf(t, doc) * idf(t)
score(doc)   = sum( tfidf(t, doc) ) for all query terms t
```

Where `N` is the total number of indexed documents and `df(t)` is the number of documents containing term `t`. The `+1` smoothing keeps IDF at least 1 for terms present in every document, preventing zero scores.

This is implemented in `SearchEngine._idf()` and `SearchEngine._tfidf()` in `src/search.py`. The raw frequency sum is still included in results as `score` for reference.

### Proximity-Aware Scoring

For multi-word queries, a small proximity bonus rewards documents where the query terms appear close together in the text:

```
proximity_bonus = PROXIMITY_ALPHA / (1 + min_distance)
```

Where `min_distance` is the smallest gap (in token positions) between any two query terms in the document, using the position data stored during indexing. `PROXIMITY_ALPHA = 0.5` keeps the bonus well below typical TF-IDF scores -- it acts as a tiebreaker rather than overriding the main score.

The final ranking key is `final_score = tfidf_score + proximity_bonus`.

Complexity: O(P^2) in stored positions per document. For the small pages on quotes.toscrape.com this is negligible.

### Query Suggestions

When a search returns no results and one or more query terms are absent from the index, the tool automatically suggests close matches using `difflib.get_close_matches` from the Python standard library:

```
>> find frend
No pages found containing all of: frend.
  Did you mean "friend" instead of "frend"?
```

Suggestions are generated per missing term and shown below the not-found message. Complexity: O(V) in vocabulary size.

### Benchmarking

The `benchmark` command runs 1000 repetitions of several sample queries against the loaded index and reports timing, without making any network requests:

```
>> benchmark
Index benchmark
  Documents         : 60
  Unique terms      : ...
  Total postings    : ...
  Avg postings/term : ...

  Query timing (1000 repetitions each):
    'love'              :   xx.x ms total  /  0.0xx ms avg
    'good'              :   xx.x ms total  /  0.0xx ms avg
```

This gives concrete evidence of index lookup speed and supports the claim that O(1) dictionary access keeps single-term queries extremely fast even with TF-IDF scoring.

### Complexity Analysis

| Operation | Complexity | Notes |
|---|---|---|
| Word lookup (`get_word`) | O(1) average | Python dictionary hash lookup |
| Single-term `find` | O(D) | D = documents containing the term |
| Multi-term `find` | O(T * D) | T = query terms; AND intersection then scoring |
| Proximity scoring | O(P^2) | P = total positions across query terms per doc |
| Query suggestions | O(V) | V = vocabulary size; scans all indexed words |
| `stats` top terms | O(V log V) | Sort over vocabulary |

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
- **Ranking:** TF-IDF with proximity is implemented. A BM25 model would handle document-length normalisation more rigorously on larger corpora.
- **No stemming:** "run", "running", and "runs" are treated as distinct terms. A stemmer (e.g. Porter Stemmer) would improve recall.
- **Single-threaded:** the crawler fetches one page at a time. Asynchronous fetching (e.g. `aiohttp`) would reduce wall-clock time, though the politeness delay already limits throughput regardless.
- **Proximity scoring cost:** the O(P^2) proximity calculation is fine for this site's small pages. It would need optimisation (e.g. sorted-merge of position lists) for larger corpora.

---

## Submission Notes

- The `data/index.json` file is generated by running `build` and is required for submission. It is not gitignored.
- The GitHub repository URL is: [https://github.com/krishsolanki1/comp3011-cw2-search-tool](https://github.com/krishsolanki1/comp3011-cw2-search-tool)
- The video demonstration link will be provided separately on the submission form.
- To reproduce the index from scratch, run `python -m src.main build` from the project root with an internet connection. The full crawl takes approximately 6 minutes.
