from __future__ import absolute_import, unicode_literals

from django.utils import timezone

import pytest

from transport import items


@pytest.fixture
def now():
    return timezone.now().replace(microsecond=0)
    # MySQL discards microseconds


@pytest.mark.django_db
def test_create_item_creates_item(now):
    item = {'body': "Text", 'timestamp': now}
    old_count = len(items.list())

    response = items.create(item)

    assert 'id' in response
    new_count = len(items.list())
    assert new_count > old_count
