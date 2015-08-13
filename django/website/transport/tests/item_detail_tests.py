from __future__ import unicode_literals, absolute_import

import pytest

from data_layer.tests.factories import ItemFactory
import transport


@pytest.fixture
def item():
    return ItemFactory()


@pytest.mark.django_db
def test_get_item_gets_item(item):
    item_data = transport.items.get(item.id)

    assert item_data['id'] == item.id
    assert item_data['body'] == item.body
