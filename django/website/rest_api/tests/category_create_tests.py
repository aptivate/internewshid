from __future__ import unicode_literals, absolute_import

import pytest

from django.core.urlresolvers import reverse
from rest_framework.test import APIRequestFactory

from taxonomies.models import Taxonomy, Term
from ..views import TaxonomyViewSet


def create_category(name):
    url = reverse('category-list')
    request = APIRequestFactory().put(url, {'name': name})
    view = TaxonomyViewSet.as_view(actions={'put': 'create'})
    return view(request, pk=id)


@pytest.mark.django_db
def test_create_a_category():

    create_category('Animal')

    assert Taxonomy.objects.count() == 1
    [taxonomy] = Taxonomy.objects.all()
    assert taxonomy.name == 'Animal'

# TODO: taxonomies have a slug

# TODO: test_get_categories


def add_term(taxonomy, term):
    pass


@pytest.mark.django_db
def test_add_term_to_taxonomy():
    create_category('Animal')

    add_term('Animal', 'dog')
    add_term('Animal', 'cat')

    [animal] = Taxonomy.objects.all()
    terms = Term.objects.all()
    assert len(terms) == 2
    assert all(term.taxonomy.name == 'Animal' for term in terms)
