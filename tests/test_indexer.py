"""Tests for extract_visible_text, tokenize, and InvertedIndex."""

from src.indexer import InvertedIndex, extract_visible_text, tokenize

# ---------------------------------------------------------------------------
# HTML fixtures
# ---------------------------------------------------------------------------

SIMPLE_HTML = """
<html>
  <head><title>Test Page</title><style>body { color: red; }</style></head>
  <body>
    <h1>Hello World</h1>
    <p>Hello again, world!</p>
    <script>var x = 1;</script>
  </body>
</html>
"""

TWO_WORD_HTML = """
<html><body><p>good good bad</p></body></html>
"""

SECOND_PAGE_HTML = """
<html><body><p>bad bad bad good</p></body></html>
"""


# ---------------------------------------------------------------------------
# extract_visible_text
# ---------------------------------------------------------------------------

def test_extract_excludes_script_content():
    text = extract_visible_text(SIMPLE_HTML)
    assert "var x" not in text


def test_extract_excludes_style_content():
    text = extract_visible_text(SIMPLE_HTML)
    assert "color: red" not in text


def test_extract_includes_body_text():
    text = extract_visible_text(SIMPLE_HTML)
    assert "Hello" in text
    assert "World" in text


# ---------------------------------------------------------------------------
# tokenize
# ---------------------------------------------------------------------------

def test_tokenize_lowercases():
    assert tokenize("Hello WORLD") == ["hello", "world"]


def test_tokenize_removes_punctuation():
    assert tokenize("hello, world!") == ["hello", "world"]


def test_tokenize_keeps_numbers():
    assert tokenize("page 2") == ["page", "2"]


def test_tokenize_no_empty_tokens():
    tokens = tokenize("   !!!   ")
    assert tokens == []


def test_tokenize_mixed_input():
    tokens = tokenize("It's a great day — really!")
    assert "it" in tokens
    assert "s" in tokens
    assert "a" in tokens
    assert "great" in tokens
    assert "day" in tokens
    assert "really" in tokens


# ---------------------------------------------------------------------------
# InvertedIndex — add_document / frequency / positions
# ---------------------------------------------------------------------------

def test_add_document_records_frequency():
    idx = InvertedIndex()
    idx.add_document("https://example.com/", TWO_WORD_HTML)
    entry = idx.get_word("good")
    assert entry["https://example.com/"]["frequency"] == 2


def test_add_document_records_positions():
    idx = InvertedIndex()
    idx.add_document("https://example.com/", TWO_WORD_HTML)
    entry = idx.get_word("good")
    positions = entry["https://example.com/"]["positions"]
    assert len(positions) == 2
    # "good" appears before "bad" so positions should be less than bad's positions
    bad_pos = idx.get_word("bad")["https://example.com/"]["positions"][0]
    assert all(p < bad_pos for p in positions)


def test_add_document_case_insensitive():
    html = "<html><body><p>Good GOOD good</p></body></html>"
    idx = InvertedIndex()
    idx.add_document("https://example.com/", html)
    assert idx.get_word("good")["https://example.com/"]["frequency"] == 3
    assert idx.get_word("Good")["https://example.com/"]["frequency"] == 3


def test_add_document_stores_title():
    idx = InvertedIndex()
    idx.add_document("https://example.com/", SIMPLE_HTML)
    assert idx._docs["https://example.com/"]["title"] == "Test Page"


def test_add_document_stores_word_count():
    idx = InvertedIndex()
    idx.add_document("https://example.com/", TWO_WORD_HTML)
    assert idx._docs["https://example.com/"]["word_count"] == 3  # good good bad


# ---------------------------------------------------------------------------
# InvertedIndex — multiple documents
# ---------------------------------------------------------------------------

def test_multiple_documents_separate_entries():
    idx = InvertedIndex()
    idx.add_document("https://example.com/page1/", TWO_WORD_HTML)
    idx.add_document("https://example.com/page2/", SECOND_PAGE_HTML)

    good_entry = idx.get_word("good")
    assert "https://example.com/page1/" in good_entry
    assert "https://example.com/page2/" in good_entry
    assert good_entry["https://example.com/page1/"]["frequency"] == 2
    assert good_entry["https://example.com/page2/"]["frequency"] == 1


def test_build_from_pages():
    pages = {
        "https://example.com/page1/": TWO_WORD_HTML,
        "https://example.com/page2/": SECOND_PAGE_HTML,
    }
    idx = InvertedIndex()
    idx.build_from_pages(pages)
    assert len(idx._docs) == 2
    assert idx.get_word("bad")["https://example.com/page2/"]["frequency"] == 3


# ---------------------------------------------------------------------------
# InvertedIndex — missing word
# ---------------------------------------------------------------------------

def test_get_word_missing_returns_empty_dict():
    idx = InvertedIndex()
    assert idx.get_word("nonexistent") == {}


# ---------------------------------------------------------------------------
# InvertedIndex — serialisation round-trip
# ---------------------------------------------------------------------------

def test_to_dict_from_dict_round_trip():
    idx = InvertedIndex()
    idx.add_document("https://example.com/page1/", TWO_WORD_HTML)
    idx.add_document("https://example.com/page2/", SECOND_PAGE_HTML)

    data = idx.to_dict()
    restored = InvertedIndex.from_dict(data)

    assert restored.get_word("good") == idx.get_word("good")
    assert restored.get_word("bad") == idx.get_word("bad")
    assert restored._docs == idx._docs


def test_from_dict_empty_data():
    idx = InvertedIndex.from_dict({})
    assert idx.get_word("anything") == {}
    assert idx._docs == {}
