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
    item = ItemFactory()
    assert Item.objects.count() == 1

    response = delete_item(item.id)

    assert status.is_success(response.status_code)
    assert Item.objects.count() == 0


def delete_items(item_ids):
    request = APIRequestFactory().delete('/items/', {'ids': item_ids})
    view = ItemViewSet.as_view()
    return view(request)


@pytest.mark.xfail  # awaiting bulk
@pytest.mark.django_db
def test_delete_items():
    ItemFactory()
    ItemFactory()
    items = list(Item.objects.all())
    assert len(items) == 2

    response = delete_items([i.id for i in items])

    assert status.is_success(response.status_code)
    assert len(Item.objects.count()) == 0
