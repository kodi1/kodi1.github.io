import pytest
from page_scraper import PageScraper


class MockLogger:
    """Simple logger for collecting messages during scraping."""

    def __call__(self, message, level=None):
        print(message)

    def info(self, message):
        print(message)


@pytest.fixture(scope="module")
def scraper():
    """PageScraper instance with real host and mock logger."""
    logger = MockLogger()
    return PageScraper(logger, "https://btvplus.bg/")


@pytest.mark.parametrize("section", [
    s for s in PageScraper.sections if s["action"] == "show_products" and s["testable"]
])
def test_get_items_returns_items(scraper, section):
    results = scraper.get_items(section["path"])

    assert len(results) > 0, "Expected at least one product to be parsed"


def test_get_nested_items_returns_items(scraper):
    products = scraper.get_items(scraper.sections[0]["path"])
    episodes = scraper.get_items(products[0]["path"])

    assert len(episodes) > 0, "Expected at least one product to be parsed"


def test_get_stream_returns_m3u(scraper):
    products = scraper.get_items(scraper.sections[0]["path"])
    episodes = scraper.get_items(products[0]["path"])
    stream = scraper.get_stream(episodes[0]["path"])

    assert "m3u" in stream["url"] or "m3u8" in stream["url"]