from __future__ import unicode_literals, absolute_import

import pytest

from django.core.urlresolvers import reverse
from rest_framework.test import APIRequestFactory
from rest_framework import status
from data_layer.models import Item
from .item_create_view_tests import create_item
from .taxonomy_and_term_create_tests import (
    create_category,
    add_term,
)
from ..views import ItemViewSet


@pytest.fixture
def category():
    return create_category(name="Ebola Questions").data


@pytest.fixture
def term(category):
    return add_term(
        taxonomy=category["slug"],
        name="Vaccine",
    ).data


@pytest.fixture
def item():
    return create_item(body="Text").data


def categorize_item(item_id, taxonomy_slug, term_name):
    url = reverse('item-add-term', kwargs={"pk": item_id})
    term = {'taxonomy': taxonomy_slug, 'name': term_name}
    request = APIRequestFactory().post(url, term)
    view = ItemViewSet.as_view(actions={'post': 'add_term'})
    return view(request, item_pk=item_id)


@pytest.mark.django_db
def test_item_can_haz_category(category, term, item):
    # Associate category with the item
    categorize_item(
        item_id=item['id'],
        taxonomy_slug=category['slug'],
        term_name=term['name'],
    )

    # Fetch the item
    # TODO: use the API for this
    [item_orm] = Item.objects.all()
    # See the category
    [term_orm] = item_orm.terms.all()
    assert term_orm.name == term['name']


# TODO test for terms with the same name in different taxonomies

@pytest.mark.django_db
def test_categorize_item_fails_gracefully_if_term_not_found(item):
    response = categorize_item(
        item_id=item['id'],
        taxonomy_slug='uknown-slug',
        term_name='unknown-term',
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert False, "further assertion about error message"
