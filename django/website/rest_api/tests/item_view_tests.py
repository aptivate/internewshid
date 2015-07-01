from __future__ import unicode_literals, absolute_import

from django.test import TestCase
from rest_framework.test import APIRequestFactory

from data_layer.tests.factories import ItemFactory

from rest_api.views import ItemList


class ItemViewTests(TestCase):

    def get(self, view_class, url):
        view = view_class.as_view()
        request = APIRequestFactory().get(url)
        return view(request)

    def test_get_items_returns_empty_if_no_items(self):
        response = self.get(ItemList, '/items/')
        self.assertEqual(response.data, [])

    def test_get_items_returns_all_items(self):
        item = ItemFactory()

        payload = self.get(ItemList, '/items/').data

        self.assertEqual(len(payload), 1)
        self.assertEqual(payload[0]['body'], item.body)
        # I don't much care for this test.
        # It's testing too much of the stack, and its messy because the payload
        # isn't the same kind data strcture even as ItemSerializer(item).data
