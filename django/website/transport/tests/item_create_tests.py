from __future__ import unicode_literals, absolute_import
import pytest

from transport.data_layer_transport import ItemTransport
from django.utils import timezone


@pytest.mark.django_db
def test_create_message_creates_item():
    item_transport = ItemTransport()
    now = timezone.now().replace(
        microsecond=0  # MySQL discards microseconds
    )
    item = {'body': "Text", 'timestamp': now}
    old_count = len(item_transport.list())

    response = item_transport.create(item)

    assert 'id' in response
    new_count = len(item_transport.list())
    assert new_count > old_count
