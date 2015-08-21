from __future__ import unicode_literals, absolute_import

import pytest

from taxonomies.tests.factories import TaxonomyFactory
from transport import items
from ..exceptions import TransportException


@pytest.fixture
def taxonomy():
    return TaxonomyFactory(
        name="Test Tags", multiplicity='multiple', vocabulary='open')


@pytest.mark.django_db
def test_multiple_new_terms_applied_to_item(taxonomy):
    item = items.create({'body': "What is the cuse of ebola?"})

    term_names = ['Monrovia', 'age 40-45', 'pertinent']

    item = items.add_terms(
        item['id'], taxonomy.slug, term_names)

    stored_names = [t['name'] for t in item['terms']]

    assert sorted(term_names) == sorted(stored_names)


@pytest.mark.django_db
def test_add_terms_raises_transport_exception_if_item_absent(taxonomy):
    unknown_item_id = 6

    term_names = ['Monrovia', 'age 40-45', 'pertinent']
    with pytest.raises(TransportException) as excinfo:
        items.add_terms(unknown_item_id, taxonomy.slug, term_names)

    error = excinfo.value.message

    assert error['status_code'] == 404
    assert error['detail'] == "Message matching query does not exist."
    assert error['item_id'] == unknown_item_id
    assert error['terms']['name'] == term_names
    assert error['terms']['taxonomy'] == taxonomy.slug


@pytest.mark.django_db
def test_add_terms_raises_transport_exception_if_taxonomy_absent():
    item = items.create({'body': "What is the cuse of ebola?"})

    term_names = ['Monrovia', 'age 40-45', 'pertinent']
    with pytest.raises(TransportException) as excinfo:
        items.add_terms(item['id'], 'unknown-slug', term_names)

    error = excinfo.value.message

    assert error['status_code'] == 400
    assert error['detail'] == "Taxonomy matching query does not exist."
    assert error['item_id'] == item['id']
    assert error['terms']['name'] == term_names
    assert error['terms']['taxonomy'] == 'unknown-slug'
