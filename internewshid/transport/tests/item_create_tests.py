from __future__ import absolute_import, unicode_literals

from datetime import datetime

from django.utils import timezone
from django.utils.dateparse import parse_datetime

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


@pytest.mark.django_db
def test_timestamp_ignores_microseconds():
    timestamp = datetime(year=2018, month=12, day=21, hour=13, minute=59,
                         second=1, microsecond=123)

    item = {'body': "Text", 'timestamp': timestamp}

    response = items.create(item)

    parsed = parse_datetime(response['timestamp'])
    assert parsed.microsecond == 0
