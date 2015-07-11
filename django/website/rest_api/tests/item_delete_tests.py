from __future__ import unicode_literals, absolute_import

import pytest

from data_layer.tests.factories import ItemFactory
from data_layer.models import Item
from rest_framework.test import APIRequestFactory
from rest_framework import status
from ..views import ItemViewSet


def delete_item(id):
    request = APIRequestFactory().delete('/')
    view = ItemViewSet.as_view(actions={'delete': 'destroy'})
    return view(request, pk=id)


@pytest.mark.django_db
def test_delete_item():
    ItemFactory(body="test1")
    item = ItemFactory()
    assert Item.objects.count() == 2

    response = delete_item(item.id)

    assert status.is_success(response.status_code)
    assert Item.objects.count() == 1
    assert Item.objects.get().body == "test1"
