from __future__ import unicode_literals, absolute_import
import pytest

from rest_api.serializers import ItemSerializer
from data_layer.tests.factories import ItemFactory
from transport import data_layer_transport as dl


@pytest.mark.django_db
def test_get_items_exists():
    items = dl.get_messages()
    assert items == []

@pytest.mark.django_db
def test_get_items_returns_items():
    item = ItemFactory(body="test")

    items = dl.get_messages()

    assert len(items) == 1
    [item] = items
    assert item['body'] == 'test'


@pytest.mark.django_db
def test_get_items_filters_by_body():
    item1 = ItemFactory(body="one")
    item2 = ItemFactory(body="two")

    items = dl.get_messages(body='one')

    assert len(items) == 1
    [item] = items
    assert item['body'] == 'one'
