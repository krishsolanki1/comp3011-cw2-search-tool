# COMP3011 Coursework 2 — Search Engine Tool

## Overview

A command-line search engine tool developed for COMP3011 Web Services and Web Data (Year 3, 2025–2026). The tool crawls a target website, builds an inverted index from the scraped content, and supports word-frequency queries and ranked full-text search.

Target website: [https://quotes.toscrape.com/](https://quotes.toscrape.com/)

> **Status:** Project skeleton complete. Implementation in progress.

---

## Project Structure

```
comp3011-cw2-search-tool/
├── src/
│   ├── __init__.py
│   ├── crawler.py      # Web crawler
│   ├── indexer.py      # Inverted index builder
│   ├── search.py       # Query and ranking logic
│   ├── storage.py      # JSON persistence
│   └── main.py         # CLI entry point
├── tests/
│   ├── test_crawler.py
│   ├── test_indexer.py
│   ├── test_search.py
│   └── test_storage.py
├── data/
│   └── index.json      # Generated index (created at runtime)
├── requirements.txt
└── README.md
```

---

## Setup

Requirements: Python 3.9+

```bash
git clone https://github.com/krishsolanki1/comp3011-cw2-search-tool.git
cd comp3011-cw2-search-tool
pip install -r requirements.txt
```

---

## Usage

```bash
# Crawl the website and build the index
python -m src.main build

# Load an existing index from disk
python -m src.main load

# Print frequency and location info for a word
python -m src.main print <word>

# Search the index for pages matching query terms
python -m src.main find <query terms>
```

---

## Testing

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=term-missing
```

---

## Design

*To be completed during implementation.*

Key components:
- **Crawler** — uses `requests` and `BeautifulSoup` to follow links from the base URL up to a configurable page limit.
- **Indexer** — builds an inverted index mapping each word to the URLs and frequency counts where it appears.
- **Searcher** — scores and ranks pages for multi-term queries; supports single-word lookup.
- **Storage** — serialises and deserialises the index as `data/index.json`.

---

## Limitations

*To be completed after implementation.*

---

## GenAI Usage Declaration

This project was developed with assistance from Generative AI tools. A full declaration — including which tools were used, for which tasks, and how outputs were reviewed and adapted — will be provided before final submission, in accordance with the COMP3011 academic integrity guidelines.

---

## Author

Student: Krish Solanki  
Module: COMP3011 Web Services and Web Data  
University of Nottingham  
Academic Year: 2025–2026
