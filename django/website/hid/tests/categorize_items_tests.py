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


@pytest.fixture
def item_list():
    for i in range(10):
        transport.items.create(
            {'body': 'test message {}'.format(i)}
        )
    return transport.items.list()


@pytest.mark.django_db
def test_add_categories_works_with_multiple_items(term, item_list):
    category_list = [
        (item['id'], term.name)
        for item in item_list
    ]

    add_categories(category_list)

    assert all(
        item_data['terms'][0]['name'] == term.name
        for item_data in transport.items.list()
    )


@pytest.mark.django_db
def test_add_categories_fails_gracefully_with_nonsense_term(item):
    category_list = [(item['id'], "Non-existant term"), ]

    with pytest.raises(transport.exceptions.TransportException):
        add_categories(category_list)


@pytest.mark.django_db
def test_add_categories_fails_gracefully_with_nonsense_item(term):
    category_list = [(6, "Non-existant term"), ]  # Who is number 1?

    with pytest.raises(transport.exceptions.TransportException):
        add_categories(category_list)
