from __future__ import unicode_literals, absolute_import

from django.test import TestCase
from rest_api.views import ItemList

from rest_framework.test import APIRequestFactory


class HandlerTests(TestCase):

    factory = APIRequestFactory()

    def test_get_items_returns_empty_if_no_items(self):
        request = self.factory.get('/items/')
        view = ItemList.as_view()
        response = view(request)
        self.assertEqual(response.data, [])
