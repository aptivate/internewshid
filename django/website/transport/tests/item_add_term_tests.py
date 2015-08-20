from __future__ import unicode_literals, absolute_import
import pytest

from data_layer.models import Item
from taxonomies.tests.factories import (
    TaxonomyFactory,
    TermFactory
)
from transport import items
from ..exceptions import TransportException


@pytest.fixture
def taxonomy():
    return TaxonomyFactory()


@pytest.fixture
def item_data():
    item = {'body': "What is the cuse of ebola?"}
    return items.create(item)


@pytest.mark.django_db
def test_terms_can_be_added_to_item(item_data):
    item_id = item_data['id']
    # TODO: Replace with Term list() ?
    item = Item.objects.get(pk=item_id)
    assert item.terms.count() == 0

    for term in (TermFactory() for i in range(2)):
        items.add_term(item_id, term.taxonomy.slug, term.name)

    assert item.terms.count() == 2


@pytest.mark.django_db
def test_add_term_fails_if_taxonomy_does_not_exist(item_data):
    with pytest.raises(TransportException) as excinfo:
        items.add_term(
            item_data['id'],
            "unknown-slug",
            "unknown term name",
        )

    error = excinfo.value.message

    assert error['status_code'] == 400
    assert error['detail'] == "Taxonomy matching query does not exist."
    assert error['term']['name'] == "unknown term name"


@pytest.mark.django_db
def test_add_term_fails_if_term_does_not_exist(taxonomy, item_data):
    with pytest.raises(TransportException) as excinfo:
        items.add_term(
            item_data['id'],
            taxonomy.slug,
            "unknown term name",
        )

    error = excinfo.value.message

    assert error['status_code'] == 400
    assert error['detail'] == "Term matching query does not exist."
    assert error['term']['name'] == "unknown term name"


@pytest.mark.django_db
def test_add_term_fails_if_item_does_not_exist():
    with pytest.raises(TransportException) as excinfo:
        term = TermFactory()
        unknown_item_id = 6  # I am a Free Man
        items.add_term(unknown_item_id, term.taxonomy.slug, term.name)

    error = excinfo.value.message

    assert error['status_code'] == 404
    assert error['detail'] == "Message matching query does not exist."
    # TODO: assert error['detail'] == "Item matching query does not exist."
    assert error['item_id'] == unknown_item_id
