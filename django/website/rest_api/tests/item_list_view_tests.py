from __future__ import unicode_literals, absolute_import

import pytest

from rest_framework.test import APIRequestFactory

from data_layer.tests.factories import ItemFactory

from rest_api.views import ItemList


def get(view_class, url, data=None):
    view = view_class.as_view()
    request = APIRequestFactory().get(url, data)
    return view(request)

@pytest.mark.django_db
def test_get_items_returns_empty_if_no_items():
    response = get(ItemList, '/items')
    assert response.data == []

@pytest.mark.django_db
def test_get_items_returns_all_items():
    item = ItemFactory()

    payload = get(ItemList, '/items').data

    assert len(payload) == 1
    assert payload[0]['body'] == item.body

@pytest.mark.django_db
def test_filter_by_body():
    item1 = ItemFactory(body="one")
    item2 = ItemFactory(body="two")
    payload = get(ItemList, '/items', {'body': 'one'}).data

    assert len(payload) == 1
    assert payload[0]['body'] == "one"
