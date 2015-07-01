from __future__ import unicode_literals, absolute_import
import pytest

from rest_api.serializers import ItemSerializer
from data_layer.tests.factories import ItemFactory
from transport import data_layer_transport as dl


@pytest.mark.django_db
def test_get_messages_exists():
    messages = dl.get_messages()
    assert messages == []

@pytest.mark.django_db
def test_get_messages_returns_items():
    item = ItemFactory(body="test")

    messages = dl.get_messages()
    [message] = messages
    assert message['body'] == 'test'

@pytest.mark.xfail
def test_store_message_uses_create():
    #message = {}
    #:l.create_message(message)
    #create.assert_called_with(message)
    assert False
