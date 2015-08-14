from __future__ import unicode_literals, absolute_import
import pytest

from transport import items
from ..exceptions import TransportException


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
def test_update_item_throws_exception_for_missing_body():
    data = {'body': "Text"}
    response = items.create(data)
    id = response['id']

    with pytest.raises(TransportException) as excinfo:
        items.update(id, {})
    assert 'body' in excinfo.value.message
