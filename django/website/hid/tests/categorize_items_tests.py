from __future__ import unicode_literals, absolute_import
import pytest

from taxonomies.tests.factories import TermFactory, TaxonomyFactory

import transport
from ..views import add_categories


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
def test_add_categories_adds_term_to_item(term, item):
    category_list = [(item['id'], term.name), ]

    add_categories(category_list)

    [item_data] = transport.items.list()
    [term_data] = item_data['terms']
    assert term_data['name'] == term.name
    assert term_data['taxonomy'] == term.taxonomy.slug
