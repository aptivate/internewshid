from __future__ import unicode_literals, absolute_import
import pytest

from data_layer.tests.factories import ItemFactory
from transport import ItemTransport


@pytest.mark.django_db
def test_list_items_exists():
    # TODO: Should ItemTransport probably be a pytest fixture?
    assert ItemTransport().list() == []


@pytest.mark.django_db
def test_list_items_returns_items():
    item = ItemFactory(body="test")

    # TODO: Should ItemTransport probably be a pytest fixture?
    items = ItemTransport().list()

    assert len(items) == 1
    [item] = items
    assert item['body'] == 'test'


@pytest.mark.django_db
def test_list_items_filters_by_body():
    ItemFactory(body="one")
    ItemFactory(body="two")

    # TODO: Should ItemTransport probably be a pytest fixture?
    items = ItemTransport().list(body='one')

    assert len(items) == 1
    [item] = items
    assert item['body'] == 'one'
