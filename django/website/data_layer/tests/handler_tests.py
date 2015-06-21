from __future__ import unicode_literals, absolute_import

from django.test import TestCase
from django.utils import timezone

from data_layer import handlers
from data_layer import models


class HandlerTests(TestCase):

    def test_message_create(self):
        now = timezone.now().replace(
            microsecond=0  # MySQL discards microseconds
        )
        inmessage = {'body': "Text", 'timestamp': now}

        handlers.Message.create(inmessage)

        outmessage = models.Message.objects.get()
        self.assertEqual(outmessage.body, "Text")
        self.assertEqual(outmessage.timestamp, now)

    def test_message_list_empty(self):
        messages = handlers.Message.list()
        self.assertEqual(len(list(messages)), 0)

    def test_message_list_one(self):
        models.Message(body="Test").save()

        [message] = handlers.Message.list()

        self.assertEqual(message['body'], "Test")

