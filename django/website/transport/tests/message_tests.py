from __future__ import unicode_literals, absolute_import

from django.test import TestCase
from django.utils import timezone

from transport import data_layer_transport as dl


# TODO use mock here to verify the handler methods are being called instead of
# verifying the store behaviour
class TransportLayerMessageTests(TestCase):

    def test_get_messages_exists(self):
        messages = dl.get_messages()
        self.assertEqual(len(list(messages)), 0)

    def test_store_messages_exists(self):
        message = dict()
        dl.store_message(message)

    def test_stored_messages_can_be_gotten(self):
        now = timezone.now().replace(
            microsecond=0  # MySQL discards microseconds
        )
        message = dict(body="Text", timestamp=now)

        dl.store_message(message)
        messagelist = list(dl.get_messages())
        [outmessage] = messagelist

        self.assertEqual(outmessage['body'], "Text")
        self.assertEqual(outmessage['timestamp'],  now)
