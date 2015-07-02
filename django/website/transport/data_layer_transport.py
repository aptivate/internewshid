from rest_framework.test import APIRequestFactory
from rest_framework import status
from rest_api.views import ItemList

from .exceptions import TransportException


def get_messages(**kwargs):  # TODO rename get_items
    request = APIRequestFactory().get('/items', kwargs)
    view = ItemList.as_view()
    return view(request).data


def create_message(item):  # TODO rename create_item
    view = ItemList.as_view()
    request = APIRequestFactory().post('/items', item)
    response = view(request)
    if status.is_success(response.status_code):
        return response.data
    else:
        response.data['status_code'] = response.status_code
        raise TransportException(response.data)
