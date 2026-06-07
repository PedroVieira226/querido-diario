from datetime import date

import pytest
from scrapy.exceptions import DropItem

from gazette.pipelines import GazetteDateFilteringPipeline


class MockSpider:
    def __init__(self, start_date=None):
        if start_date:
            self.start_date = start_date


@pytest.fixture
def pipeline():
    """Fixture para inicializar o pipeline antes de cada teste."""
    return GazetteDateFilteringPipeline()


def test_should_pass_item_if_spider_has_no_start_date(pipeline):
    spider = MockSpider()
    item = {"date": date(2026, 1, 1), "title": "Diário Oficial"}

    result = pipeline.process_item(item, spider)

    assert result == item


def test_should_pass_item_if_date_is_after_or_equal_to_start_date(pipeline):
    spider = MockSpider(start_date=date(2026, 1, 1))
    item = {"date": date(2026, 1, 5), "title": "Diário Oficial Novo"}

    result = pipeline.process_item(item, spider)

    assert result == item


def test_should_drop_item_if_date_is_before_start_date(pipeline):
    start_limit = date(2026, 1, 10)
    spider = MockSpider(start_date=start_limit)
    item = {"date": date(2026, 1, 5), "title": "Diário Oficial Antigo"}

    with pytest.raises(DropItem) as exc_info:
        pipeline.process_item(item, spider)

    assert str(exc_info.value) == f"Droping all items before {start_limit}"
