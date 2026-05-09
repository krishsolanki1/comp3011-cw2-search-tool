# COMP3011 CW2 -- Video Script

**Target length:** 5 minutes (advanced features add ~25 seconds; trim GenAI section slightly if needed)
**Format:** Screen recording with voiceover

---

## 0:00 -- 0:20 | Introduction

"Hi, I'm Krish Solanki, this is my COMP3011 Coursework 2 submission. I've built a command-line search engine tool in Python that crawls quotes.toscrape.com, builds an inverted index, and supports word-frequency lookups and multi-term ranked search. I'll walk through a live demo, explain the design, show the tests, and then reflect on how I used AI tools."

---

## 0:20 -- 2:00 | Live Demo

**[Open terminal, navigate to project folder, run the shell]**

"I'll start by opening the interactive shell."

```
python -m src.main
```

**[Type `help`]**

"The shell supports build, load, print, find, stats, and exit. The index has already been built, so I'll load it directly rather than crawling again -- which would take about a minute due to the six-second politeness delay."

**[Type `load`]**

"The index loads instantly from the saved JSON file. Ten pages indexed, eight hundred and forty-five unique terms."

**[Type `print good`]**

"The `print` command shows the inverted index entry for a word -- which pages it appears on, the frequency on each page, and the exact token positions."

**[Type `print xyzzy`]**

"If the word isn't in the index, it tells me clearly rather than silently returning nothing."

**[Type `find indifference`]**

"The `find` command searches for pages containing a term. Results are ranked using TF-IDF -- rare terms are weighted more heavily than common ones."

**[Type `find good friends`]**

"For multi-word queries, only pages containing all terms are returned -- AND logic. The output shows the TF-IDF score, a proximity bonus for terms that appear close together, and the final combined score."

**[Type `find frend`]**

"If a query term isn't in the index but something similar is, the tool suggests the closest match. That's using Python's difflib module against the full vocabulary."

**[Type `find bananaaaaa`]**

"A completely unrecognisable term returns a clean message with no spurious suggestion."

**[Type `find` with no terms]**

"An empty query is handled gracefully."

**[Type `stats`]**

"The stats command now shows total postings, the top ten terms by corpus frequency, and a timestamp if the index was built with the current version."

**[Type `benchmark`]**

"The benchmark command runs one thousand repetitions of several sample queries and reports timing. No network requests -- it just measures how fast the index lookup and TF-IDF scoring actually are. Sub-millisecond per query, which is what you'd expect from O(1) dictionary access."

**[Type `exit`]**

---

## 2:00 -- 3:15 | Code and Design Walkthrough

**[Open `src/crawler.py` in the editor]**

"The crawler uses `requests` and `BeautifulSoup`. It follows the `li.next` pagination link on each page, sleeps for six seconds between fetches to be polite, and stops if a URL has already been visited or a request fails. I injected the sleep function as a parameter so tests can replace it with a no-op -- no test ever waits six seconds."

**[Open `src/indexer.py`]**

"The indexer first strips script, style, and head tags from the HTML, then extracts the remaining text and tokenises it using the regex `[a-z0-9]+` -- which lowercases everything and removes punctuation in one step. Each token's position in the document is recorded, so the index stores both frequency and positions per URL."

"The index structure looks like this: word, then URL, then frequency and a list of positions. Document metadata -- title and word count -- is stored separately."

**[Open `src/search.py`]**

"The searcher normalises the query with the same tokeniser so search is always case-insensitive. For multi-word queries, it intersects the URL sets across all terms -- AND logic -- then scores each candidate using TF-IDF. IDF gives rare terms a higher weight, so a page with one occurrence of 'indifference' can outrank a page with three occurrences of 'the'. A proximity bonus uses the stored position data to reward documents where the query terms appear close together. The bonus is capped small enough that it's a tiebreaker, not a score override."

**[Open `src/storage.py`]**

"Storage is straightforward -- JSON with indentation for readability. The load function raises `FileNotFoundError` if the file is missing and `ValueError` for corrupt JSON, so the caller always gets a clear error rather than a silent failure."

---

## 3:15 -- 3:45 | Testing

**[Run in terminal]**

```
pytest --cov=src --cov-report=term-missing
```

"One hundred and seventeen tests, ninety-seven percent line coverage. The crawler tests mock the HTTP session entirely and replace the sleep function, so they run in milliseconds. The indexer tests check tokenisation, frequency counts, position accuracy, multiple documents, and round-trip serialisation. The search tests cover single and multi-word queries, case insensitivity, AND logic, ranking order, and output formatting. There is also an integration test that runs a complete fake pipeline -- fake HTML pages in, search results out -- without touching the network at all."

---

## 3:45 -- 4:10 | Git History

**[Run in terminal]**

```
git log --oneline --graph --decorate -n 12
```

"You can see the commit history follows a clear progression: initial scaffold, then each component committed separately -- crawler, indexer, storage, search, the CLI shell, then tests and documentation. Each commit message uses a conventional prefix so the history is easy to read."

---

## 4:10 -- 5:00 | GenAI Critical Evaluation

"I used Claude as an AI assistant throughout this project. I want to be honest about what that actually involved, because just saying 'I used AI' doesn't capture the nuance."

"When I described the project structure, the AI suggested sensible module boundaries and a reasonable class layout. That saved time on scaffolding. But when it suggested the crawler, the first draft had no domain restriction -- a next link pointing to an external site would have been followed. I caught that because I was reading the requirements carefully and I added the `urlparse` check myself."

"The AI wrote test scaffolding quickly, but it missed some edge cases on the first attempt. It didn't initially include a test for an empty query, and it didn't test that the sleeper is never called when there's only one page. I added those because I thought about the behaviour, not because the AI flagged them."

"Probably the most useful thing the AI did was make me articulate my design clearly. When I described what I wanted, the AI would produce something, and reviewing that output forced me to notice where my own thinking had been vague."

"The most important thing to say is that accepting a suggestion is not the same as understanding it. Every function in this project I can explain, the tests I can describe, and the design decisions I can justify. The AI accelerated the process but it didn't replace the understanding."

---

## Closing

"That covers the full submission. The repository is public on GitHub, the index file is committed, and the README has full setup and usage instructions. Thanks for watching."
