from __future__ import unicode_literals, absolute_import

import pytest

from rest_framework.test import APIRequestFactory
from rest_framework import status

from ..serializers import TermSerializer
from ..views import (
    TaxonomyViewSet,
    TermViewSet,
)
from taxonomies.tests.factories import (
    TaxonomyFactory,
    TermFactory,
)


def create_category(**kwargs):
    request = APIRequestFactory().put("", kwargs)
    view = TaxonomyViewSet.as_view(actions={'put': 'create'})

    response = view(request)
    assert status.is_success(response.status_code), response.data

    return response


def taxonomy_exists(name):
    taxonomies = get_taxonomies().data

    names = [t['name'] for t in taxonomies]

    return name in names


def term_exists(long_name, slug):
    terms = get_terms(slug).data
    names = [t['long_name'] for t in terms]

    return long_name in names


def count_taxonomies():
    return len(get_taxonomies().data)


def get_taxonomies():
    request = APIRequestFactory().get("")
    view = TaxonomyViewSet.as_view(actions={'get': 'list'})
    response = view(request)
    assert status.is_success(response.status_code), response.data

    return response


def get_terms(taxonomy_slug):
    request = APIRequestFactory().get("", data={'taxonomy': taxonomy_slug})
    view = TermViewSet.as_view(actions={'get': 'list'})
    response = view(request)
    assert status.is_success(response.status_code), response.data

    return response


@pytest.mark.django_db
def test_create_a_category():
    category = "Test Ebola Questions"

    old_count = count_taxonomies()
    assert not taxonomy_exists(category)

    response = create_category(name=category)
    assert status.is_success(response.status_code), response.data

    new_count = count_taxonomies()
    assert new_count - old_count == 1

    assert taxonomy_exists(category)


# TODO: write test for getting taxonomies and terms, so we can re-write all
# these tests using only the API (as Functional tests)

def add_term(**kwargs):
    """
        taxonomy: string with taxonomy name
        term: name of term
    """
    request = APIRequestFactory().post("", kwargs)
    view = TermViewSet.as_view(actions={'post': 'create'})
    response = view(request)
    assert status.is_success(response.status_code), response.data

    return response


@pytest.mark.django_db
def test_add_term_to_taxonomy():
    # TODO: Use API to create taxonomy
    taxonomy = TaxonomyFactory(name='Test Ebola Questions')

    response1 = add_term(taxonomy=taxonomy.slug, name='Vaccine')
    response2 = add_term(taxonomy=taxonomy.slug, name='Time')

    assert status.is_success(response1.status_code), response1.data
    assert status.is_success(response2.status_code), response2.data
    terms = get_terms(taxonomy.slug).data
    assert len(terms) == 2

    assert all(term['taxonomy'] == taxonomy.slug for term in terms)


@pytest.mark.django_db
def test_terms_have_long_name():
    # TODO: Use API to create taxonomy
    taxonomy = TaxonomyFactory(name="Ebola Questions")

    vacc_long_name = "Is there a vaccine?"

    assert not term_exists(vacc_long_name, taxonomy.slug)

    response = add_term(
        taxonomy=taxonomy.slug,
        name="Test Vaccine",
        long_name=vacc_long_name
    )

    assert status.is_success(response.status_code), response.data

    assert term_exists(vacc_long_name, taxonomy.slug)


@pytest.mark.django_db
def test_id_field_not_in_serialized_terms():
    # TODO: Use API to create term
    term = TermFactory()

    serialzed = TermSerializer(term).data

    assert 'id' not in serialzed
