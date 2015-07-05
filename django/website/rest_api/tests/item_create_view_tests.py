from __future__ import unicode_literals, absolute_import

import pytest

from django.utils import timezone
from rest_framework.test import APIRequestFactory
from rest_framework import status

from rest_api.views import ItemViewSet


def create(item):
    request = APIRequestFactory().post('/items', item)
    view = ItemViewSet.as_view(actions={'post': 'create'})
    return view(request)


@pytest.mark.django_db
def test_create_item():
    item = {'body': "Text"}
    response = create(item)

    assert status.is_success(response.status_code)
    assert response.data['body'] == "Text"


@pytest.mark.django_db
def test_create_item_with_timestamp():
    now = timezone.now().replace(
        microsecond=0  # MySQL discards microseconds
    )
    item = {'body': "Text", 'timestamp': now}

    response = create(item)

    assert status.is_success(response.status_code)
