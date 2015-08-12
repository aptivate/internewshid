from __future__ import unicode_literals, absolute_import
import pytest

from django.core.urlresolvers import reverse

from rest_framework.test import APIRequestFactory
from rest_framework import status

from rest_api.views import ItemViewSet

from .item_create_view_tests import create_item
from .item_list_view_tests import get as list_items


def update_item(id, **kwargs):
    url = '/items/%d' % id  # Not used as we call the view directly
    request = APIRequestFactory().post(url, kwargs)
    view = ItemViewSet.as_view(actions={'post': 'update'})

    response = view(request, pk=id)
    assert status.is_success(response.status_code), response.data

    return response


@pytest.mark.django_db
def test_item_fields_can_be_updated():
    old_data = {'body': 'That the government is using this Ebola as a business to inrich few governmemt official',
                'network_provider': '8737 (Lonestar)'}
    new_data = {'body': 'That the government is using this Ebola as a business to inrich few government official',
                'network_provider': '8737 (CellCom)'}

    response = create_item(**old_data)
    id = response.data['id']

    update_item(id, **new_data)

    [item] = list_items().data

    assert item['body'] == new_data['body']
    assert item['network_provider'] == new_data['network_provider']

# TODO: Test terms
# TODO: Test timestamp updated
