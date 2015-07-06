from __future__ import unicode_literals, absolute_import
import pytest

from data_layer.tests.factories import ItemFactory
from transport.data_layer_transport import ItemTransport


@pytest.mark.django_db
def test_delete_item():
    item_transport = ItemTransport()  # TODO: Should probably be a pytest fixture?
    item = ItemFactory()
    assert len(item_transport.list()) == 1

    item_transport.delete(item.id)

    assert len(item_transport.list()) == 0
