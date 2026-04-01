# COMP3011 Coursework 2 — Search Engine Tool

## Project Overview

This project is a command-line search engine tool developed for COMP3011 Web Services and Web Data (Year 3). The tool crawls a target website, builds an inverted index from the scraped content, and supports word-frequency queries and full-text search over the indexed data.

Target website: [https://quotes.toscrape.com/](https://quotes.toscrape.com/)

> **Status:** Project structure initialised. Implementation not yet started.

---

## Planned Features

- Web crawler to scrape pages from the target website
- Inverted index builder storing word frequencies and source URLs
- Persistent index stored as `data/index.json`
- CLI commands:
  - `build` — crawl the website and build the index
  - `load` — load an existing index from disk
  - `print <word>` — display the frequency and locations of a given word
  - `find <query terms>` — search the index and return ranked results

---

## Planned Setup

Requirements:
- Python 3.9+
- pip

```bash
# Clone the repository
git clone https://github.com/<your-username>/comp3011-cw2-search-tool.git
cd comp3011-cw2-search-tool

# Install dependencies
pip install -r requirements.txt
```

---

## Planned Usage

```bash
# Build the index by crawling the website
python -m src build

# Load an existing index
python -m src load

# Print frequency info for a word
python -m src print <word>

# Search for pages matching query terms
python -m src find <query terms>
```

---

## Planned Testing

Tests will be written using `pytest` and located in the `tests/` directory. Coverage will be measured with `pytest-cov`.

```bash
# Run tests
pytest

# Run tests with coverage report
pytest --cov=src
```

---

## Project Structure

```
comp3011-cw2-search-tool/
├── src/               # Main source code
├── tests/             # Unit and integration tests
├── data/              # Generated index file (index.json)
├── docs/              # Additional documentation
├── requirements.txt   # Python dependencies
└── README.md          # This file
```

---

## GenAI Declaration

This project may involve the use of Generative AI tools (e.g. GitHub Copilot, Claude) during development. All AI-assisted contributions will be declared here upon submission, in accordance with the module's academic integrity guidelines.

> *Declaration to be completed before final submission.*

---

## Author

Student: Krish Solanki  
Module: COMP3011 Web Services and Web Data  
Academic Year: 2025–2026
