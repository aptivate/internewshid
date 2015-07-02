from __future__ import unicode_literals, absolute_import

import pytest

from django.utils import timezone
from rest_framework.test import APIRequestFactory
from rest_framework import status

from rest_api.views import ItemList


@pytest.mark.django_db
def test_create_item():
    item = {'body': "Text"}
    request = APIRequestFactory().post('/items', item)
    view = ItemList.as_view()

    response = view(request)

    assert status.is_success(response.status_code)
    assert response.data['body'] == "Text"


@pytest.mark.django_db
def test_create_item_with_timestamp():
    now = timezone.now().replace(
        microsecond=0  # MySQL discards microseconds
    )
    item = {'body': "Text", 'timestamp': now}
    request = APIRequestFactory().post('/items', item)
    view = ItemList.as_view()

    response = view(request)

    assert status.is_success(response.status_code)
