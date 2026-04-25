# COMP3011 CW2 -- Marking Checklist

Use this to confirm each marking criterion has evidence in the submission.

---

## Crawling

| Criterion | Evidence | Location |
|---|---|---|
| Crawls target website | `Crawler.crawl()` fetches all pages of quotes.toscrape.com | `src/crawler.py` |
| Follows pagination | Parses `li.next > a` and uses `urljoin` for relative URLs | `src/crawler.py:_next_url()` |
| Politeness delay | `time.sleep(delay_seconds)` called between fetches, default 6s | `src/crawler.py:crawl()` |
| Avoids duplicate URLs | Checked against `pages` dict before fetching | `src/crawler.py:crawl()` |
| Stays on target domain | `urlparse` check against `_allowed_host` | `src/crawler.py:_next_url()` |
| Handles network errors | `requests.RequestException` caught, prints message, stops cleanly | `src/crawler.py:_fetch()` |
| User-Agent header | Session header set to a descriptive string | `src/crawler.py:__init__()` |

---

## Indexing

| Criterion | Evidence | Location |
|---|---|---|
| Builds inverted index | `InvertedIndex.build_from_pages()` processes all crawled pages | `src/indexer.py` |
| Stores word frequency | `frequency` counter per URL per word | `src/indexer.py:add_document()` |
| Stores word positions | `positions` list (token index in document) per URL per word | `src/indexer.py:add_document()` |
| Case-insensitive | `text.lower()` before regex tokenisation | `src/indexer.py:tokenize()` |
| Removes punctuation | Regex `[a-z0-9]+` discards all non-alphanumeric characters | `src/indexer.py:tokenize()` |
| Excludes script/style | BeautifulSoup `.decompose()` on skip tags before text extraction | `src/indexer.py:extract_visible_text()` |
| Stores document metadata | `word_count` and `title` per URL in `_docs` | `src/indexer.py:add_document()` |
| Round-trip serialisation | `to_dict()` / `from_dict()` tested | `src/indexer.py`, `tests/test_indexer.py` |

---

## Storage and Load

| Criterion | Evidence | Location |
|---|---|---|
| Saves index to disk | `save_index()` writes JSON with `indent=2` | `src/storage.py` |
| Loads index from disk | `load_index()` reads and parses JSON | `src/storage.py` |
| Default path `data/index.json` | `INDEX_PATH = Path("data/index.json")` | `src/storage.py` |
| Parent directories created | `dest.parent.mkdir(parents=True, exist_ok=True)` | `src/storage.py:save_index()` |
| Clear error if file missing | Raises `FileNotFoundError` with path in message | `src/storage.py:load_index()` |
| Clear error for corrupt JSON | Raises `ValueError` wrapping `json.JSONDecodeError` | `src/storage.py:load_index()` |
| Index file committed | `data/index.json` tracked in repository | `data/index.json` |

---

## Search

| Criterion | Evidence | Location |
|---|---|---|
| `print <word>` command | Calls `format_word_entry()`, shows frequency and positions | `src/search.py`, `src/main.py` |
| `find <query>` command | Calls `find()`, returns ranked list | `src/search.py`, `src/main.py` |
| Case-insensitive search | `normalise_query()` lowercases before lookup | `src/search.py` |
| Multi-word AND logic | URL set intersection across all query terms | `src/search.py:find()` |
| Frequency-based ranking | Results sorted by summed term frequency descending | `src/search.py:find()` |
| Missing word handled | Returns empty dict / friendly message | `src/search.py:get_word_entry()` |
| Empty query handled | Returns empty list / friendly message | `src/search.py:find()`, `format_find_results()` |
| Result format | URL, score, matched terms, per-term frequencies | `src/search.py:find()` |

---

## Testing

| Criterion | Evidence | Location |
|---|---|---|
| Unit tests present | 95 tests across 5 test files | `tests/` |
| Tests do not hit live site | HTTP mocked with `MagicMock` session | `tests/test_crawler.py` |
| Tests do not sleep | Sleep replaced with no-op function | `tests/test_crawler.py` |
| Crawler tests | Pagination, duplicates, sleep calls, errors, domain restriction, User-Agent | `tests/test_crawler.py` (10 tests) |
| Indexer tests | Text extraction, tokenisation, frequency, positions, multiple docs, serialisation | `tests/test_indexer.py` (18 tests) |
| Search tests | Single/multi-word, case, AND logic, ranking, formatting, edge cases | `tests/test_search.py` (22 tests) |
| Storage tests | Save, load, round-trip, missing file, corrupt JSON, parent dirs | `tests/test_storage.py` (10 tests) |
| CLI tests | All helper functions, interactive shell commands, one-shot dispatch | `tests/test_main.py` (35 tests) |
| Integration test | Fake crawl output to index to search -- end-to-end pipeline | `tests/test_main.py:test_full_pipeline_fake_pages` |
| Line coverage | 98% overall, 100% on indexer/search/storage | `pytest --cov=src` |

---

## Code Quality

| Criterion | Evidence | Location |
|---|---|---|
| Type annotations | All function signatures typed throughout | `src/*.py` |
| Docstrings | Module, class, and method docstrings on all public interfaces | `src/*.py` |
| Readable naming | Snake case, descriptive variable and function names | Throughout |
| Single responsibility | Each module does one thing (crawl / index / search / store / CLI) | `src/` |
| No bare exceptions | Only `requests.RequestException` caught where appropriate | `src/crawler.py` |
| No hardcoded secrets | No credentials or tokens in code | Throughout |
| Testability by design | Crawler accepts injected session and sleeper; storage accepts custom paths | `src/crawler.py`, `src/storage.py` |

---

## Git History

| Criterion | Evidence |
|---|---|
| Repository is public | https://github.com/krishsolanki1/comp3011-cw2-search-tool |
| Clean commit history | 10 commits with conventional prefix messages |
| Incremental commits | One commit per feature: scaffold, crawler, indexer, storage, search, CLI, tests, docs |
| Commit messages | `feat:`, `chore:`, `test:`, `docs:` prefixes used consistently |
| No large binary blobs | Only source, JSON index, and docs committed |

**Commit log:**

```
da62368  chore: add verification scripts and compiled index
5bd1376  docs: polish README with setup usage and design rationale
160b821  test: expand coverage for search tool components
6d4e38c  feat: add interactive command-line shell
6b36a7b  feat: implement print and find search logic
5a15837  feat: add JSON index persistence
ed33073  feat: build inverted index with word statistics
af3a28a  feat: implement polite crawler for quotes site
aec9964  chore: add initial search tool skeleton
adbffe1  Initial project scaffold for COMP3011 CW2 Search Engine Tool
```

---

## Video

| Criterion | Plan |
|---|---|
| Live demo of all commands | `build`, `load`, `print`, `find`, `stats`, `exit` shown in demo |
| Multi-word query shown | `find good friends` demonstrates AND logic and ranking |
| Edge cases shown | `print nonsense`, `find bananaaaaa`, empty `find` |
| Code walkthrough | crawler, indexer, search, storage briefly explained |
| Testing shown | `pytest --cov` output shown live |
| Git history shown | `git log --oneline --graph --decorate` shown live |
| GenAI critical evaluation | Specific examples, honest limitations discussed |
| Script | `docs/video_script.md` |
| Demo commands | `docs/demo_commands.txt` |

---

## GenAI Reflection

| Criterion | Evidence |
|---|---|
| Declared use of AI | README GenAI section, video script section at 4:10 |
| Specific tools named | Claude (Anthropic) |
| Honest about what AI did | Scaffolding, class layout, test suggestions, README wording |
| Critical evaluation | AI missed domain restriction bug, missed empty-query test, missed single-page sleep test |
| Student responsibility stated | All code reviewed, tested, and understood; student directed design decisions |

---

## Submission Checklist

- [ ] GitHub repository is public
- [ ] `data/index.json` is committed and valid
- [ ] `README.md` contains setup, usage, design, testing, and GenAI sections
- [ ] `pytest` passes with 95 tests and 98% coverage
- [ ] Video is 5 minutes or under
- [ ] Video link submitted separately on the submission form
- [ ] GitHub URL submitted on the submission form
