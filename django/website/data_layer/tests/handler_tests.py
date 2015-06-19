from __future__ import unicode_literals, absolute_import
from datetime import datetime

from django.test.testcases import SimpleTestCase

from data_layer import handlers


class HandlerTests(SimpleTestCase):

    def test_message_post_handler(self):
        message = dict(body="Text", timestamp=datetime.now())
        handlers.post_message(message)
