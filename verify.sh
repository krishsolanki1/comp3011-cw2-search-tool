#!/usr/bin/env bash
# verify.sh -- Quick setup and test script for Linux/macOS
# Usage: bash verify.sh

set -e

echo "=== COMP3011 Search Engine Tool -- Verification ==="
echo ""

# Create virtual environment if it does not already exist
if [ ! -d ".venv" ]; then
    echo "[1/4] Creating virtual environment..."
    python3 -m venv .venv
else
    echo "[1/4] Virtual environment already exists."
fi

# Activate and install dependencies
echo "[2/4] Installing dependencies..."
source .venv/bin/activate
pip install --quiet -r requirements.txt

# Run tests with coverage
echo "[3/4] Running tests with coverage..."
echo ""
pytest --cov=src --cov-report=term-missing
echo ""

# Usage reminder
echo "[4/4] Setup complete. To use the tool:"
echo ""
echo "  source .venv/bin/activate"
echo ""
echo "  python -m src.main              # open interactive shell"
echo "  python -m src.main build        # crawl and build the index"
echo "  python -m src.main load         # load a saved index"
echo "  python -m src.main print <word> # look up a word"
echo "  python -m src.main find <terms> # search for pages"
echo ""
echo "Note: 'build' makes real HTTP requests with a 6-second delay between pages."
