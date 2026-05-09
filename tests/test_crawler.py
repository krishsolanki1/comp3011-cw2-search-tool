"""Tests for the Crawler class."""

import pytest
from src.crawler import Crawler


def test_crawler_instantiation():
    crawler = Crawler(base_url="https://quotes.toscrape.com/")
    assert crawler.base_url == "https://quotes.toscrape.com/"
    assert crawler.max_pages == 50


def test_crawler_crawl_not_implemented():
    crawler = Crawler(base_url="https://quotes.toscrape.com/")
    with pytest.raises(NotImplementedError):
        crawler.crawl()
