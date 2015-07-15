from __future__ import unicode_literals, absolute_import

import pytest

from django.core.urlresolvers import reverse
from rest_framework.test import APIRequestFactory
from rest_framework import status

from taxonomies.models import Taxonomy, Term
from ..views import (
    TaxonomyViewSet,
    TermViewSet,
)


def create_category(name):
    url = reverse('taxonomy-list')
    request = APIRequestFactory().put(url, {'name': name})
    view = TaxonomyViewSet.as_view(actions={'put': 'create'})
    return view(request, pk=id)


@pytest.mark.django_db
def test_create_a_category():

    response = create_category('Ebola Questions')

    assert status.is_success(response.status_code), response.data
    assert Taxonomy.objects.count() == 1
    [taxonomy] = Taxonomy.objects.all()
    assert taxonomy.name == 'Ebola Questions'


# TODO: test_get_categories


def add_term(**kwargs):
    """
        taxonomy: string with taxonomy name
        term: name of term
    """
    url = reverse('term-list')
    request = APIRequestFactory().post(url, kwargs)
    view = TermViewSet.as_view(actions={'post': 'create'})
    return view(request)


@pytest.mark.django_db
def test_add_term_to_taxonomy():
    create_category('Ebola Questions')
    [category] = Taxonomy.objects.all()

    response1 = add_term(taxonomy=category.slug, name='Vaccine')
    response2 = add_term(taxonomy=category.slug, name='Time')

    assert status.is_success(response1.status_code), response1.data
    assert status.is_success(response2.status_code), response2.data
    terms = Term.objects.all()
    assert len(terms) == 2
    assert all(term.taxonomy.name == category.name for term in terms)
