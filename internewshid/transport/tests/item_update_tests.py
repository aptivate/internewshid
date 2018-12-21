from __future__ import absolute_import, unicode_literals

import datetime

import pytest

from transport import items
from ..exceptions import ItemNotUniqueException


@pytest.mark.django_db
def test_update_item_updates_item():
    data = {'body': "Text"}
    response = items.create(data)
    id = response['id']

    data['body'] = "Updated text"
    response = items.update(id, data)

    # TODO: Update to use items.get() when ready
    assert len(items.list(body="Text")) == 0

    [updated_item] = items.list(body="Updated text")

    assert updated_item['id'] == id


@pytest.mark.django_db
def test_cannot_update_item_to_have_non_unique_body_and_timestamp():
    item_1 = {
        'timestamp': datetime.datetime.now(),
        'body': "Text"
    }

    item_2 = {
        'timestamp': datetime.datetime.now(),
        'body': "Text 2"
    }

    item_1 = items.create(item_1)
    item_2 = items.create(item_2)

    item_2['timestamp'] = item_1['timestamp']
    item_2['body'] = item_1['body']

    id = item_2.pop('id')

    with pytest.raises(ItemNotUniqueException):
        items.update(id, item_2)


@pytest.mark.django_db
def test_timestamp_ignores_microseconds():
    timestamp = datetime.datetime(
        year=2018, month=12, day=21,
        hour=13, minute=59, second=1, microsecond=123
    )

    data = {'body': "Text", 'timestamp': timestamp}

    item = items.create(data)

    data['timestamp'] = timestamp.replace(microsecond=456)

    response = items.update(item['id'], data)

    assert response['timestamp'] == '2018-12-21T13:59:01Z'
