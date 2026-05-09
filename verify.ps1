# verify.ps1 -- Quick setup and test script for Windows PowerShell
# Usage: .\verify.ps1

Write-Host "=== COMP3011 Search Engine Tool -- Verification ===" -ForegroundColor Cyan
Write-Host ""

# Create virtual environment if it does not already exist
if (-Not (Test-Path ".venv")) {
    Write-Host "[1/4] Creating virtual environment..."
    python -m venv .venv
} else {
    Write-Host "[1/4] Virtual environment already exists."
}

# Activate and install dependencies
Write-Host "[2/4] Installing dependencies..."
& .\.venv\Scripts\Activate.ps1
pip install --quiet -r requirements.txt

# Run tests with coverage
Write-Host "[3/4] Running tests with coverage..."
Write-Host ""
pytest --cov=src --cov-report=term-missing
Write-Host ""

# Usage reminder
Write-Host "[4/4] Setup complete. To use the tool:" -ForegroundColor Green
Write-Host ""
Write-Host "  .\.venv\Scripts\Activate.ps1"
Write-Host ""
Write-Host "  python -m src.main              # open interactive shell"
Write-Host "  python -m src.main build        # crawl and build the index"
Write-Host "  python -m src.main load         # load a saved index"
Write-Host "  python -m src.main print <word> # look up a word"
Write-Host "  python -m src.main find <terms> # search for pages"
Write-Host ""
Write-Host "Note: 'build' makes real HTTP requests with a 6-second delay between pages."
