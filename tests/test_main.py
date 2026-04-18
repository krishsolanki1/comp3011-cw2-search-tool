"""Tests for main.py CLI helpers and one-shot entry point.

All tests are unit-level: no live network requests, no real sleeps,
no writes to the real data/ directory.
"""

from unittest.mock import MagicMock, patch

from src.indexer import InvertedIndex
from src.main import _build, _find, _load, _print_word, _stats, main
from src.search import SearchEngine

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

PAGE1 = "<html><head><title>P1</title></head><body><p>good good bad</p></body></html>"
PAGE2 = "<html><head><title>P2</title></head><body><p>bad friends</p></body></html>"


def _make_engine() -> SearchEngine:
    idx = InvertedIndex()
    idx.add_document("https://quotes.toscrape.com/", PAGE1)
    idx.add_document("https://quotes.toscrape.com/page/2/", PAGE2)
    return SearchEngine(idx)


# ---------------------------------------------------------------------------
# _print_word
# ---------------------------------------------------------------------------

def test_print_word_no_engine_prints_message(capsys):
    _print_word(None, "good")
    assert "No index loaded" in capsys.readouterr().out


def test_print_word_known_word(capsys):
    _print_word(_make_engine(), "good")
    out = capsys.readouterr().out
    assert "good" in out
    assert "frequency" in out


def test_print_word_unknown_word(capsys):
    _print_word(_make_engine(), "zzznonsense")
    assert "No index entry" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# _find
# ---------------------------------------------------------------------------

def test_find_no_engine_prints_message(capsys):
    _find(None, "good")
    assert "No index loaded" in capsys.readouterr().out


def test_find_with_results(capsys):
    _find(_make_engine(), "good")
    out = capsys.readouterr().out
    assert "quotes.toscrape.com" in out


def test_find_no_results(capsys):
    _find(_make_engine(), "zzznonsense")
    assert "No pages found" in capsys.readouterr().out


def test_find_empty_query(capsys):
    _find(_make_engine(), "")
    assert "at least one" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# _stats
# ---------------------------------------------------------------------------

def test_stats_no_engine_prints_message(capsys):
    _stats(None)
    assert "No index loaded" in capsys.readouterr().out


def test_stats_with_engine(capsys):
    _stats(_make_engine())
    out = capsys.readouterr().out
    assert "Pages indexed" in out
    assert "Unique terms" in out


# ---------------------------------------------------------------------------
# _load
# ---------------------------------------------------------------------------

def test_load_missing_file_prints_message(capsys, tmp_path):
    engine_ref = [None]
    missing = tmp_path / "no_index.json"
    with patch("src.main.INDEX_PATH", missing):
        _load(engine_ref)
    assert "No index file found" in capsys.readouterr().out
    assert engine_ref[0] is None


def test_load_existing_file_sets_engine(tmp_path):
    engine_ref = [None]
    idx = InvertedIndex()
    idx.add_document("https://quotes.toscrape.com/", PAGE1)
    data = idx.to_dict()

    index_file = tmp_path / "index.json"
    import json
    index_file.write_text(json.dumps(data), encoding="utf-8")

    with patch("src.main.INDEX_PATH", index_file), \
         patch("src.main.index_exists", return_value=True), \
         patch("src.main.load_index", return_value=data):
        _load(engine_ref)

    assert engine_ref[0] is not None
    assert isinstance(engine_ref[0], SearchEngine)


def test_load_prints_summary(capsys, tmp_path):
    idx = InvertedIndex()
    idx.add_document("https://quotes.toscrape.com/", PAGE1)
    data = idx.to_dict()

    with patch("src.main.INDEX_PATH", tmp_path / "index.json"), \
         patch("src.main.index_exists", return_value=True), \
         patch("src.main.load_index", return_value=data):
        engine_ref = [None]
        _load(engine_ref)

    out = capsys.readouterr().out
    assert "loaded" in out.lower()


# ---------------------------------------------------------------------------
# _build
# ---------------------------------------------------------------------------

def test_build_no_pages_prints_message(capsys):
    engine_ref = [None]
    mock_crawler = MagicMock()
    mock_crawler.crawl.return_value = {}
    with patch("src.main.Crawler", return_value=mock_crawler):
        _build(engine_ref)
    assert "no pages" in capsys.readouterr().out.lower()
    assert engine_ref[0] is None


def test_build_saves_index_and_sets_engine(tmp_path, capsys):
    engine_ref = [None]
    fake_pages = {
        "https://quotes.toscrape.com/": PAGE1,
        "https://quotes.toscrape.com/page/2/": PAGE2,
    }
    mock_crawler = MagicMock()
    mock_crawler.crawl.return_value = fake_pages

    with patch("src.main.Crawler", return_value=mock_crawler), \
         patch("src.main.INDEX_PATH", tmp_path / "index.json"), \
         patch("src.main.save_index") as mock_save:
        _build(engine_ref)

    assert engine_ref[0] is not None
    assert mock_save.called
    out = capsys.readouterr().out
    assert "saved" in out.lower()


# ---------------------------------------------------------------------------
# main() — one-shot command dispatch
# ---------------------------------------------------------------------------

def test_main_no_args_calls_run_shell():
    with patch("src.main.run_shell") as mock_shell:
        main([])
        mock_shell.assert_called_once()


def test_main_unknown_command_prints_message(capsys):
    main(["notacommand"])
    assert "Unknown command" in capsys.readouterr().out


def test_main_print_no_word_prints_usage(capsys):
    with patch("src.main.index_exists", return_value=False):
        main(["print"])
    assert "Usage" in capsys.readouterr().out


def test_main_find_no_terms_prints_usage(capsys):
    with patch("src.main.index_exists", return_value=False):
        main(["find"])
    assert "Usage" in capsys.readouterr().out


def test_main_build_dispatches():
    engine_ref_capture = []

    def fake_build(engine_ref):
        engine_ref_capture.append(engine_ref)

    with patch("src.main._build", side_effect=fake_build):
        main(["build"])

    assert len(engine_ref_capture) == 1


def test_main_stats_no_index(capsys):
    with patch("src.main.index_exists", return_value=False):
        main(["stats"])
    assert "No index" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# run_shell — interactive loop via patched input()
# ---------------------------------------------------------------------------

def _run_shell_with_inputs(*commands: str, engine=None):
    """Drive run_shell() by feeding it a sequence of input lines then EOF."""
    inputs = iter(list(commands))

    def fake_input(*_):
        try:
            return next(inputs)
        except StopIteration:
            raise EOFError

    engine_ref_seen = []

    # Patch _build/_load so they don't do real work, but record engine_ref
    def fake_build(engine_ref):
        engine_ref_seen.append(engine_ref)

    def fake_load(engine_ref):
        if engine is not None:
            engine_ref[0] = engine
        engine_ref_seen.append(engine_ref)

    from src import main as main_mod
    with patch("builtins.input", side_effect=fake_input), \
         patch.object(main_mod, "_build", side_effect=fake_build), \
         patch.object(main_mod, "_load", side_effect=fake_load):
        from src.main import run_shell
        run_shell()

    return engine_ref_seen


def test_shell_exit_command(capsys):
    from src.main import run_shell
    with patch("builtins.input", side_effect=["exit"]):
        run_shell()
    assert "Goodbye" in capsys.readouterr().out


def test_shell_quit_command(capsys):
    from src.main import run_shell
    with patch("builtins.input", side_effect=["quit"]):
        run_shell()
    assert "Goodbye" in capsys.readouterr().out


def test_shell_eof_exits_gracefully(capsys):
    from src.main import run_shell
    with patch("builtins.input", side_effect=EOFError):
        run_shell()
    assert "Exiting" in capsys.readouterr().out


def test_shell_help_command(capsys):
    from src.main import run_shell
    with patch("builtins.input", side_effect=["help", "exit"]):
        run_shell()
    assert "Commands" in capsys.readouterr().out


def test_shell_empty_line_ignored(capsys):
    from src.main import run_shell
    with patch("builtins.input", side_effect=["", "exit"]):
        run_shell()
    assert "Goodbye" in capsys.readouterr().out


def test_shell_unknown_command(capsys):
    from src.main import run_shell
    with patch("builtins.input", side_effect=["notacommand", "exit"]):
        run_shell()
    assert "Unknown command" in capsys.readouterr().out


def test_shell_print_no_word(capsys):
    from src.main import run_shell
    with patch("builtins.input", side_effect=["print", "exit"]):
        run_shell()
    assert "Usage" in capsys.readouterr().out


def test_shell_find_no_terms(capsys):
    from src.main import run_shell
    with patch("builtins.input", side_effect=["find", "exit"]):
        run_shell()
    assert "Usage" in capsys.readouterr().out


def test_shell_build_dispatches():
    from src import main as main_mod
    called = []
    with patch("builtins.input", side_effect=["build", "exit"]), \
         patch.object(main_mod, "_build", side_effect=lambda ref: called.append(True)):
        from src.main import run_shell
        run_shell()
    assert called


def test_shell_load_dispatches():
    from src import main as main_mod
    called = []
    with patch("builtins.input", side_effect=["load", "exit"]), \
         patch.object(main_mod, "_load", side_effect=lambda ref: called.append(True)):
        from src.main import run_shell
        run_shell()
    assert called


def test_shell_stats_dispatches(capsys):
    from src.main import run_shell
    with patch("builtins.input", side_effect=["stats", "exit"]):
        run_shell()
    assert "No index loaded" in capsys.readouterr().out


def test_shell_print_word_dispatches(capsys):
    from src.main import run_shell
    with patch("builtins.input", side_effect=["print hello", "exit"]):
        run_shell()
    # No engine loaded → friendly message
    assert "No index loaded" in capsys.readouterr().out


def test_shell_find_dispatches(capsys):
    from src.main import run_shell
    with patch("builtins.input", side_effect=["find good times", "exit"]):
        run_shell()
    assert "No index loaded" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# Crawler error print (line 40 — _fetch exception branch)
# ---------------------------------------------------------------------------

def test_crawler_fetch_error_prints_message(capsys):
    import requests
    from src.crawler import Crawler
    session = MagicMock()
    session.get.side_effect = requests.ConnectionError("boom")
    crawler = Crawler(base_url="https://quotes.toscrape.com/", session=session,
                      sleeper=lambda _: None)
    result = crawler.crawl()
    assert result == {}
    assert "request failed" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# Integration test: crawl → index → search (no live network, no real sleep)
# ---------------------------------------------------------------------------

def test_full_pipeline_fake_pages():
    """End-to-end: fake crawl output → index → search → ranked results."""
    fake_pages = {
        "https://quotes.toscrape.com/": """
            <html><head><title>Page 1</title></head>
            <body><p>love is a great thing love conquers all</p></body></html>
        """,
        "https://quotes.toscrape.com/page/2/": """
            <html><head><title>Page 2</title></head>
            <body><p>love and friendship are bonds</p></body></html>
        """,
        "https://quotes.toscrape.com/page/3/": """
            <html><head><title>Page 3</title></head>
            <body><p>wisdom is knowing what you do not know</p></body></html>
        """,
    }

    # Build index
    idx = InvertedIndex()
    idx.build_from_pages(fake_pages)
    engine = SearchEngine(idx)

    # Single-word search
    results = engine.find("love")
    urls = {r["url"] for r in results}
    assert "https://quotes.toscrape.com/" in urls
    assert "https://quotes.toscrape.com/page/2/" in urls
    assert "https://quotes.toscrape.com/page/3/" not in urls

    # Page 1 has "love" twice → should rank above page 2
    assert results[0]["url"] == "https://quotes.toscrape.com/"

    # Multi-word AND search
    multi = engine.find("love friendship")
    assert len(multi) == 1
    assert multi[0]["url"] == "https://quotes.toscrape.com/page/2/"

    # Word absent from all pages
    assert engine.find("zzznonsense") == []

    # Round-trip serialisation preserves search results
    import json
    serialised = json.dumps(idx.to_dict())
    restored = InvertedIndex.from_dict(json.loads(serialised))
    engine2 = SearchEngine(restored)
    assert engine2.find("love") == engine.find("love")
