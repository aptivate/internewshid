from __future__ import unicode_literals, absolute_import

import pytest

from rest_framework.test import APIRequestFactory

from rest_api.views import ItemList


@pytest.mark.django_db
def test_create_item():
    item = {'body': "Text"}
    request = APIRequestFactory().post('/items', item)
    view = ItemList.as_view()

    response = view(request)

    assert response.status_code == 201
    assert response.data['body'] == "Text"
