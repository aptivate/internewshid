from __future__ import unicode_literals, absolute_import

import pytest

from django.core.urlresolvers import reverse
from rest_framework.test import APIRequestFactory
from rest_framework import status

from taxonomies.models import Term
from ..serializers import TermSerializer
from ..views import (
    TaxonomyViewSet,
    TermViewSet,
)
from taxonomies.tests.factories import (
    TaxonomyFactory,
    TermFactory,
)


def create_category(name):
    url = reverse('taxonomy-list')
    request = APIRequestFactory().put(url, {'name': name})
    view = TaxonomyViewSet.as_view(actions={'put': 'create'})
    return view(request, pk=id)


def taxonomy_exists(name):
    taxonomies = get_taxonomies().data

    names = [t['name'] for t in taxonomies]

    return name in names


def count_taxonomies():
    return len(get_taxonomies().data)


def get_taxonomies():
    url = reverse('taxonomy-list')
    request = APIRequestFactory().get(url)
    view = TaxonomyViewSet.as_view(actions={'get': 'list'})
    response = view(request)
    assert status.is_success(response.status_code), response.data

    return response


@pytest.mark.django_db
def test_create_a_category():
    category = "Test Ebola Questions"

    old_count = count_taxonomies()
    assert not taxonomy_exists(category)

    response = create_category(category)
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
    url = reverse('term-list')
    request = APIRequestFactory().post(url, kwargs)
    view = TermViewSet.as_view(actions={'post': 'create'})
    response = view(request)
    assert status.is_success(response.status_code), response.data

    return response


@pytest.mark.django_db
def test_add_term_to_taxonomy():
    taxonomy = TaxonomyFactory(name='Test Ebola Questions')

    response1 = add_term(taxonomy=taxonomy.slug, name='Vaccine')
    response2 = add_term(taxonomy=taxonomy.slug, name='Time')

    assert status.is_success(response1.status_code), response1.data
    assert status.is_success(response2.status_code), response2.data
    terms = Term.objects.filter(taxonomy=taxonomy)
    assert len(terms) == 2
    assert all(term.taxonomy.name == taxonomy.name for term in terms)


@pytest.mark.django_db
def test_terms_have_long_name():
    taxonomy = TaxonomyFactory(name="Ebola Questions")

    vacc_long_name = "Is there a vaccine?"

    assert not Term.objects.filter(long_name=vacc_long_name).exists()

    response = add_term(
        taxonomy=taxonomy.slug,
        name="Test Vaccine",
        long_name=vacc_long_name
    )

    assert status.is_success(response.status_code), response.data

    assert Term.objects.filter(long_name=vacc_long_name).exists()



@pytest.mark.django_db
def test_id_field_not_in_serialized_terms():
    term = TermFactory()

    serialzed = TermSerializer(term).data

    assert 'id' not in serialzed
