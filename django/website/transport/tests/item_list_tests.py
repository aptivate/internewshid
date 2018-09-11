from __future__ import unicode_literals, absolute_import

from datetime import datetime
import pytest

from data_layer.tests.factories import ItemFactory
import transport


@pytest.mark.django_db
def test_list_items_exists():
    assert transport.items.list() == []


@pytest.mark.django_db
def test_list_items_returns_items():
    item = ItemFactory(body="test")
    items = transport.items.list()
    assert len(items) == 1
    [item] = items
    assert item['body'] == 'test'


@pytest.mark.django_db
def test_list_items_filters_by_body():
    ItemFactory(body="one")
    ItemFactory(body="two")
    items = transport.items.list(body='one')
    assert len(items) == 1
    [item] = items
    assert item['body'] == 'one'


@pytest.mark.django_db
def test_date_fields_are_converted_to_datetimes():
    stored_item = ItemFactory()
    retrieved_items = transport.items.list()
    [retrieved_item] = retrieved_items
    date_fields = ('timestamp', 'created', 'last_modified')
    for date_field in date_fields:
        assert isinstance(retrieved_item[date_field], datetime)


@pytest.mark.django_db
def test_null_date_field_not_converted_to_datetime():
    ItemFactory(timestamp=None)
    retrieved_items = transport.items.list()
    [retrieved_item] = retrieved_items
    assert retrieved_item['timestamp'] is None
