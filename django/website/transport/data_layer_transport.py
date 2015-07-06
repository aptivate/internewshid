from django.core.urlresolvers import reverse
from rest_framework.test import APIRequestFactory
from rest_framework import status
from rest_api.views import ItemViewSet

from .exceptions import TransportException


class ItemTransport(object):

    url_name = 'item-list'
    actions = {
        'get': 'list',
        'post': 'create',
        'delete': 'destroy',
    }
    request_factory = APIRequestFactory()

    @property
    def url(self):
        return reverse(self.url_name)

    @classmethod
    def get_view(cls):
        return ItemViewSet.as_view(actions=cls.actions)

    def list(self, **kwargs):
        """ Return a list of Items

        If keyword arguments are given, they are used
        to filter the Items.
        """
        # FIXME: currently only body exact filtering is supported
        view = self.get_view()
        request = self.request_factory.get(self.url, kwargs)
        return view(request).data

    def create(self, item):
        """ Create an Item from the given dict """
        view = self.get_view()
        request = self.request_factory.post(self.url, item)
        response = view(request)
        if status.is_success(response.status_code):
            return response.data
        else:
            response.data['status_code'] = response.status_code
            raise TransportException(response.data)

    def delete(self, id):
        """ Delete the Item wit the given ID """
        view = self.get_view()
        url = '/items/{}/'.format(id)
        request = self.request_factory.delete(url)
        return view(request, pk=id)

    def bulk_delete(self, ids):
        """ Delete all Items whose ids appear in the given list """
        pass


def get_messages(**kwargs):  # TODO rename get_items
    return ItemTransport().list(**kwargs)


def create_message(item):  # TODO rename create_item
    return ItemTransport().create(item)


def delete_item(message_id):
    return ItemTransport().delete(message_id)


def delete_items(message_ids):
    # Message.delete_items(message_ids)
    # TODO: reimplement with API
    pass
