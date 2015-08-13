from __future__ import unicode_literals, absolute_import

import pytest

from data_layer.tests.factories import ItemFactory
import transport
from ..exceptions import TransportException


@pytest.fixture
def item():
    return ItemFactory()


@pytest.mark.django_db
def test_get_item_gets_item(item):
    item_data = transport.items.get(item.id)

    assert item_data['id'] == item.id
    assert item_data['body'] == item.body


@pytest.mark.django_db
def test_get_item_throws_exception_for_unknown_id():
    UNKNOWN_ITEM_ID = 6  # I am not a prisoner
    with pytest.raises(TransportException) as excinfo:
        item_data = transport.items.get(UNKNOWN_ITEM_ID)

    assert excinfo.value.message['detail'] == 'Not found.'
