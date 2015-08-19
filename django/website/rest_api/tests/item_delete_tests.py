from __future__ import unicode_literals, absolute_import

import pytest

from rest_framework.test import APIRequestFactory
from rest_framework import status
from ..views import ItemViewSet

from .item_create_view_tests import create_item
from .item_list_view_tests import get as list_items


def delete_item(id):
    request = APIRequestFactory().delete('/')
    view = ItemViewSet.as_view(actions={'delete': 'destroy'})
    return view(request, pk=id)


def count_items():
    items = list_items().data
    return len(items)


@pytest.mark.django_db
def test_delete_item():
    create_item(body="test1")
    item = create_item(body="test2")
    assert count_items() == 2

    response = delete_item(item.data['id'])
    assert status.is_success(response.status_code)
    assert count_items() == 1

    [item] = list_items().data
    assert item['body'] == "test1"
