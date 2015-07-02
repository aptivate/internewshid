from __future__ import unicode_literals, absolute_import

import pytest

from django.test import TestCase
from django.utils import timezone

from data_layer import handlers
from data_layer import models


class HandlerTests(TestCase):

    # Remove these tests and move to API
    def test_message_create(self):
        now = timezone.now().replace(
            microsecond=0  # MySQL discards microseconds
        )
        inmessage = {'body': "Text", 'timestamp': now}

        handlers.Message.create(inmessage)

        outmessage = models.Message.objects.get()
        self.assertEqual(outmessage.body, "Text")
        self.assertEqual(outmessage.timestamp, now)


#====== pytest tests =======
@pytest.mark.django_db
def test_item_delete():
    models.Message(body="Test").save()
    [message] = handlers.Message.list()

    handlers.Message.delete(message['id'])

    messages = handlers.Message.list()
    assert len(list(messages)) == 0


@pytest.mark.django_db
def test_messages_delete():
    models.Message(body="Test").save()
    models.Message(body="Test").save()

    messages = list(handlers.Message.list())
    assert len(list(messages)) == 2

    ids = [msg['id'] for msg in messages]
    handlers.Message.delete_items(ids)

    messages = handlers.Message.list()
    assert len(list(messages)) == 0
