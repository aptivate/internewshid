from __future__ import unicode_literals, absolute_import
from datetime import datetime

from django.test.testcases import SimpleTestCase

from transport import data_layer_transport as dl


class TransportLayerMessageTests(SimpleTestCase):

    def test_get_messages_exists(self):
        messages = dl.get_messages()
        self.assertEqual(len(messages), 0)

    def test_store_messages_exists(self):
        message = dict()
        dl.store_message(message)

    def test_stored_messages_can_be_gotten(self):
        now = datetime.now()
        message = dict(body="Text", timestamp=now)

        dl.store_message(message)
        messages = dl.get_messages()

        self.assertEqual(len(messages), 1)
        outmessage = messages[1]
        self.assertEqual(outmessage['body'], "Text")
        self.assertEqual(outmessage['timestamp'],  now)
