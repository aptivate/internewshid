from __future__ import unicode_literals, absolute_import
import pytest

from django.core.urlresolvers import reverse
from django.test import RequestFactory
from taxonomies.tests.factories import TermFactory, TaxonomyFactory

import transport
from .views_tests import fix_messages
from ..views import add_items_categories


ReqFactory = RequestFactory()


@pytest.fixture
def term():
    # TODO rewrite using transport.terms, etc.
    taxonomy = TaxonomyFactory(name="Ebola Questions")
    return TermFactory(taxonomy=taxonomy, name="Vacciene")


@pytest.fixture
def item():
    data = {'body': 'test message'}
    return transport.items.create(data)


@pytest.mark.django_db
def test_add_items_categories_adds_term_to_item(term, item):
    url = reverse('data-view-process')
    request = ReqFactory.post(url, {'a': 'b'})
    request = fix_messages(request)

    add_items_categories(request, [item['id']], term.name)

    [item_data] = transport.items.list()
    [term_data] = item_data['terms']
    assert term_data['name'] == term.name
    assert term_data['taxonomy'] == term.taxonomy.slug
