from __future__ import unicode_literals, absolute_import
import pytest

from data_layer.tests.factories import ItemFactory
from transport.data_layer_transport import ItemTransport


@pytest.mark.django_db
def test_list_items_exists():
    item_transport = ItemTransport()  # TODO: Should probably be a pytest fixture?
    items = item_transport.list()
    assert items == []


@pytest.mark.django_db
def test_list_items_returns_items():
    item_transport = ItemTransport()  # TODO: Should probably be a pytest fixture?
    item = ItemFactory(body="test")

    items = item_transport.list()

    assert len(items) == 1
    [item] = items
    assert item['body'] == 'test'


@pytest.mark.django_db
def test_list_items_filters_by_body():
    item_transport = ItemTransport()  # TODO: Should probably be a pytest fixture?
    ItemFactory(body="one")
    ItemFactory(body="two")

    items = item_transport.list(body='one')

    assert len(items) == 1
    [item] = items
    assert item['body'] == 'one'
