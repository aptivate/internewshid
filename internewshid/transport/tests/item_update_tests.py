from __future__ import absolute_import, unicode_literals

import pytest

from transport import items


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
