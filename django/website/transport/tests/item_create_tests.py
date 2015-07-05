from __future__ import unicode_literals, absolute_import
import pytest

from transport import data_layer_transport as dl
from django.utils import timezone


@pytest.mark.django_db
def test_create_message_creates_item():
    now = timezone.now().replace(
        microsecond=0  # MySQL discards microseconds
    )
    item = {'body': "Text", 'timestamp': now}
    old_count = len(dl.get_messages())

    response = dl.create_message(item)

    assert 'id' in response
    new_count = len(dl.get_messages())
    assert new_count > old_count
