from __future__ import unicode_literals, absolute_import
import pytest

from transport import items
from django.utils import timezone


@pytest.mark.django_db
def test_create_message_creates_item():
    now = timezone.now().replace(
        microsecond=0  # MySQL discards microseconds
    )
    item = {'body': "Text", 'timestamp': now}
    old_count = len(items.list())

    response = items.create(item)

    assert 'id' in response
    new_count = len(items.list())
    assert new_count > old_count
