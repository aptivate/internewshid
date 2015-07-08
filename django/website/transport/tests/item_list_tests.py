from __future__ import unicode_literals, absolute_import
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
