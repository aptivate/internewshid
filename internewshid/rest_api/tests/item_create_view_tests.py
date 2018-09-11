from __future__ import absolute_import, unicode_literals

from django.utils import timezone

import pytest
from rest_framework import status
from rest_framework.test import APIRequestFactory

from rest_api.views import ItemViewSet


def create_item(**kwargs):
    request = APIRequestFactory().post('/items', kwargs)
    view = ItemViewSet.as_view(actions={'post': 'create'})
    response = view(request)
    assert status.is_success(response.status_code), response.data

    return response


@pytest.mark.django_db
def test_create_item():
    response = create_item(body="Text")

    assert status.is_success(response.status_code)
    assert response.data['body'] == "Text"


@pytest.mark.django_db
def test_create_item_with_timestamp():
    now = timezone.now().replace(
        microsecond=0  # MySQL discards microseconds
    )

    response = create_item(body="Text", timestamp=now)

    assert status.is_success(response.status_code)
