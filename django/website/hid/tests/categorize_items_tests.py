from __future__ import unicode_literals, absolute_import
import pytest

from django.core.urlresolvers import reverse
from django.test import RequestFactory
from taxonomies.tests.factories import TermFactory, TaxonomyFactory

import transport
from .views_tests import fix_messages
from hid.tabs.view_and_edit_table import _add_items_categories


ReqFactory = RequestFactory()


@pytest.fixture
def term():
    # TODO rewrite using transport.terms, etc.
    taxonomy = TaxonomyFactory(name="Test Ebola Questions")
    return TermFactory(taxonomy=taxonomy, name="Vaccine")


@pytest.fixture
def terms():
    # TODO rewrite using transport.terms, etc.
    taxonomy = TaxonomyFactory(name="Test Ebola Questions")
    return [
        TermFactory(taxonomy=taxonomy, name="Vacciene"),
        TermFactory(taxonomy=taxonomy, name="Origin")
    ]


@pytest.fixture
def items():
    return [
        transport.items.create({'body': 'test message one'}),
        transport.items.create({'body': 'test message two'})
    ]


@pytest.fixture
def item():
    return transport.items.create({'body': 'test message one'})


@pytest.mark.django_db
def test_add_categories_adds_term_to_item(term, item):
    category_list = [(item['id'], term.taxonomy.slug, term.name), ]

    url = reverse('data-view-process')
    request = ReqFactory.post(url, {'a': 'b'})
    request = fix_messages(request)
    _add_items_categories(request, category_list)

    [item_data] = transport.items.list()
    [term_data] = item_data['terms']
    assert term_data['name'] == term.name
    assert term_data['taxonomy'] == term.taxonomy.slug


@pytest.mark.django_db
def test_add_items_categories_adds_term_to_items(terms, items):
    url = reverse('data-view-process')
    request = ReqFactory.post(url, {'a': 'b'})
    request = fix_messages(request)

    expected = {
        items[0]['id']: terms[0],
        items[1]['id']: terms[1]
    }

    category_map = [
        (item_id, term.taxonomy.slug, term.name)
        for item_id, term in expected.items()
    ]
    _add_items_categories(request, category_map)

    fetched_items = transport.items.list()
    found = 0
    for item in fetched_items:
        if item['id'] in expected:
            found += 1
            assert len(item['terms']) == 1
            [term_data] = item['terms']
            assert term_data['name'] == expected[item['id']].name
            assert term_data['taxonomy'] == expected[item['id']].taxonomy.slug

    assert found == 2
