from __future__ import unicode_literals, absolute_import
from mock import patch

from django.test import TestCase

from transport import data_layer_transport as dl


class TransportLayerMessageTests(TestCase):

    @patch('data_layer.handlers.Message.list')
    def test_get_messages_uses_list(self, list):
        list.return_value = []
        messages = dl.get_messages()
        self.assertEqual(messages, [])
        list.assert_called_with()

    @patch('data_layer.handlers.Message.create')
    def test_store_message_uses_create(self, create):
        message = {}
        dl.store_message(message)
        create.assert_called_with(message)
