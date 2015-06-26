from __future__ import unicode_literals, absolute_import
from mock import patch

from django.test import TestCase
from rest_api.views import ItemList

from rest_framework.test import APIRequestFactory


class HandlerTests(TestCase):

    factory = APIRequestFactory()

    # TODO: mock handler.Item.list() to return something plausible and check
    # that gets returned.
    @patch('data_layer.handlers.Message.list')
    def test_get_items(self, message_list):
        message_list.return_value = []

        request = self.factory.get('/items/')
        view = ItemList.as_view()
        response = view(request)

        self.assertEqual(response.data, [])
