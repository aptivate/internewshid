from __future__ import unicode_literals, absolute_import

import pytest

from rest_framework.test import APIRequestFactory
from rest_framework import status

from .item_create_view_tests import create_item
from .taxonomy_and_term_create_tests import create_taxonomy
from ..views import ItemViewSet


@pytest.fixture
def item():
    return create_item(body="Text").data


def get_item(id):
    view = ItemViewSet.as_view(actions={'get': 'retrieve'})
    request = APIRequestFactory().get('')

    return view(request, pk=id)


def get_add_free_terms_response(item_id, terms):
    request = APIRequestFactory().post('', terms)
    view = ItemViewSet.as_view(actions={'post': 'add_terms'})
    response = view(request, item_pk=item_id)

    return response


def add_free_terms_to_item(item_id, terms):
    response = get_add_free_terms_response(item_id, terms)
    assert status.is_success(response.status_code), response.data

    return response


@pytest.mark.django_db
def test_multiple_new_terms_applied_to_item(item):
    taxonomy = create_taxonomy(name='test tags',
                               vocabulary='open',
                               multiplicity='multiple').data

    slug = taxonomy['slug']
    terms = {
        'taxonomy': slug,
        'name': ['Monrovia', 'age 35-40'],
    }

    add_free_terms_to_item(item['id'], terms)

    updated_item = get_item(item['id']).data

    new_terms = []
    for term in updated_item['terms']:
        if term['taxonomy'] == slug:
            new_terms.append(term['name'])

    assert len(new_terms) > 0, "No terms created with taxonomy '%s'" % slug
    assert 'Monrovia' in new_terms
    assert 'age 35-40' in new_terms


@pytest.mark.django_db
def test_add_free_terms_returns_404_if_item_not_found():
    unknown_item_id = 6
    response = get_add_free_terms_response(unknown_item_id, {})

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data['detail'] == "Message matching query does not exist."


@pytest.mark.django_db
def test_add_free_terms_returns_400_if_taxonomy_not_found(item):
    terms = {
        'taxonomy': 'unknown-slug',
        'name': ['Monrovia', 'age 35-40'],
    }

    response = get_add_free_terms_response(item['id'], terms)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['detail'] == "Taxonomy matching query does not exist."
