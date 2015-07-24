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
    response = create_category(name="Test Ebola Questions")
    assert status.is_success(response.status_code), response.data

    return response.data


def term_for(taxonomy, name):
    """ Create, and return a Term in the given taxonomy """
    response = add_term(
        taxonomy=taxonomy['slug'],
        name=name,
    )
    assert status.is_success(response.status_code), response.data

    return response.data


@pytest.fixture
def term(category):
    return term_for(category, 'Vaccine')


@pytest.fixture
def second_term(category):
    return term_for(category, 'Timescales')


@pytest.fixture
def item():
    return create_item(body="Text").data


def categorize_item(item, term):
    url = reverse('item-add-term', kwargs={"pk": item['id']})
    request = APIRequestFactory().post(url, term)
    view = ItemViewSet.as_view(actions={'post': 'add_term'})
    return view(request, item_pk=item['id'])


@pytest.mark.django_db
def test_item_can_haz_category(term, item):
    # Associate category with the item
    categorize_item(item, term)

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
        item,
        {'taxonomy': 'unknown-slug', 'name': 'unknown-term'},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['detail'] == "Term matching query does not exist."


@pytest.mark.django_db
def test_only_one_category_per_item_per_taxonomy(item, term, second_term):
    """
        At the time of writing, all taxonomies are categories
        so there's no need yet to test that the taxonomy is a
        catagory one. Ultimately this test  sould be called something like
        test_cardinality_constraints_on_taxonomies, and maybe move them
        all to their own file. They should set the cardinality constraint
        on the Taxonmy object to optional for these tests.
    """
    categorize_item(item, term)
    categorize_item(item, second_term)

    # TODO: use the API for this
    [item_orm] = Item.objects.all()
    terms = item_orm.terms.all()
    assert len(terms) == 1
    assert terms[0].name == second_term['name']
