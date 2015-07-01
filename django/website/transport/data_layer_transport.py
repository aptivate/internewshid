from rest_framework.test import APIRequestFactory

from data_layer.handlers import Message
from rest_api.views import ItemList


def get_messages():
    request = APIRequestFactory().get('/items')
    view = ItemList.as_view()
    return view(request).data

def create_message(message):
    Message.create(message)
