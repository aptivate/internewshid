from rest_framework.test import APIRequestFactory

from rest_api.views import ItemList


def get_messages(**kwargs):  # TODO rename get_items
    request = APIRequestFactory().get('/items', kwargs)
    view = ItemList.as_view()
    return view(request).data


def create_message(item):  # TODO rename create_item
    view = ItemList.as_view()
    request = APIRequestFactory().post('/items', item)
    return view(request)
