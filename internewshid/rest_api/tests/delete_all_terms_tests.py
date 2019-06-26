from __future__ import absolute_import, unicode_literals

import pytest
from rest_framework import status
from rest_framework.test import APIRequestFactory

from data_layer.models import Item

from ..views import ItemViewSet
from .categorize_items_tests import categorize_item
from .item_delete_tests import delete_item


def remove_categories_from_item(_item, taxonomy):
    request = APIRequestFactory().post("", {'taxonomy': taxonomy})
    view = ItemViewSet.as_view(actions={'post': 'delete_all_terms'})
    return view(request, item_pk=_item['id'])


@pytest.mark.django_db  # noqa
def test_all_item_categories_can_be_deleted(item, term):
    categorize_item(item, term)

    # TODO: use the API for this
    [item_orm] = Item.objects.all()
    terms = item_orm.terms.all()
    assert len(terms) == 1

    response = remove_categories_from_item(item, term['taxonomy'])
    assert status.is_success(response.status_code), response.data

    terms = item_orm.terms.all()
    assert len(terms) == 0


@pytest.mark.django_db  # noqa
def test_error_when_deleting_terms_from_non_existent_item(item, term):
    categorize_item(item, term)
    delete_item(item['id'])

    response = remove_categories_from_item(item, term['taxonomy'])

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data['detail'] == "Message matching query does not exist."


@pytest.mark.django_db  # noqa
def test_error_when_taxonomy_does_not_exist(item, term):
    categorize_item(item, term)
    response = remove_categories_from_item(item, 'provinces-of-liberia')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['detail'] == "Taxonomy with slug 'provinces-of-liberia' does not exist."
