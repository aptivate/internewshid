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
    [item] = items
    assert item['body'] == 'test'
