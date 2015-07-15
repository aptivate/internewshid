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

    create_category('Animal')

    assert Taxonomy.objects.count() == 1
    [taxonomy] = Taxonomy.objects.all()
    assert taxonomy.name == 'Animal'


# TODO: test_get_categories


def add_term(taxonomy, term):
    """
        taxonomy: string with taxonomy name
        term: name of term
    """
    url = reverse('term-list')
    term = {
        'name': term,
        'taxonomy_name': taxonomy,
    }
    request = APIRequestFactory().post(url, term)
    view = TermViewSet.as_view(actions={'post': 'create'})
    return view(request)


@pytest.mark.django_db
def test_add_term_to_taxonomy():
    create_category('Animal')

    response1 = add_term('Animal', 'dog')
    response2 = add_term('Animal', 'cat')

    assert status.is_success(response1.status_code)
    assert status.is_success(response2.status_code)
    [animal] = Taxonomy.objects.all()
    terms = Term.objects.all()
    assert len(terms) == 2
    assert all(term.taxonomy.name == 'Animal' for term in terms)
