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
        inmessage = dict(body="Text", timestamp=now)

        handlers.Message.create(inmessage)

        outmessage = models.Message.objects.get()
        self.assertEqual(outmessage.body, "Text")
        self.assertEqual(outmessage.timestamp, now)
