from datetime import date, datetime
from unittest.mock import patch

import pytest

from gazette.pipelines import DefaultValuesPipeline


class MockSpider:
    def __init__(self, territory_id=None):
        if territory_id:
            self.TERRITORY_ID = territory_id


@pytest.fixture
def pipeline():
    """Fixture para inicializar o pipeline antes de cada teste."""
    return DefaultValuesPipeline()


def test_should_add_territory_id_from_spider(pipeline):
    spider = MockSpider(territory_id=12345)

    item = {"date": date(2026, 6, 7)}

    result = pipeline.process_item(item, spider)

    assert result["territory_id"] == 12345


def test_should_convert_date_field_to_string(pipeline):
    spider = MockSpider(territory_id=42)
    original_date = date(2026, 1, 5)
    item = {"date": original_date}

    result = pipeline.process_item(item, spider)

    assert result["date"] == str(original_date)
    assert isinstance(result["date"], str)


def test_should_add_scraped_at_timestamp_with_utc_iso_format(pipeline):
    spider = MockSpider(territory_id=42)
    item = {"date": date(2026, 1, 5)}

    fake_now = datetime(2026, 6, 7, 12, 0, 0)
    expected_timestamp = fake_now.isoformat("T") + "Z"

    with patch("datetime.datetime") as mock_datetime:
        mock_datetime.utcnow.return_value = fake_now

        result = pipeline.process_item(item, spider)

    assert result["scraped_at"] == expected_timestamp


def test_should_raise_error_if_spider_has_no_territory_id(pipeline):
    spider = MockSpider()
    item = {"date": date(2026, 1, 5)}

    with pytest.raises(AttributeError):
        pipeline.process_item(item, spider)
