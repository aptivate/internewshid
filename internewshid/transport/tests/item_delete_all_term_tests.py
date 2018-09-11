from __future__ import absolute_import, unicode_literals

import pytest

from data_layer.models import Item
from taxonomies.tests.factories import TermFactory
from transport import items

from ..exceptions import TransportException


@pytest.fixture
def item_data():
    item = {'body': "What is the cuse of ebola?"}
    return items.create(item)


@pytest.mark.django_db
def test_terms_can_be_removed_from_item(item_data):
    item_id = item_data['id']
    # TODO: Replace with Term list() ?
    item = Item.objects.get(pk=item_id)
    assert item.terms.count() == 0

    term = TermFactory(name='term to be deleted')
    items.add_terms(item_id, term.taxonomy.slug, term.name)

    term2 = TermFactory(name='term not to be deleted')
    items.add_terms(item_id, term2.taxonomy.slug, term2.name)

    assert item.terms.count() == 2

    response = items.delete_all_terms(item_id, term.taxonomy.slug)
    assert 'id' in response

    [remaining_term] = item.terms.all()

    assert remaining_term == term2


@pytest.mark.django_db
def test_fails_if_taxonomy_does_not_exist(item_data):
    item_id = item_data['id']

    with pytest.raises(TransportException) as excinfo:
        items.delete_all_terms(item_id, 'a-taxonomy-that-does-not-exist')

    error = excinfo.value.message

    assert error['status_code'] == 400
    assert error['detail'] == "Taxonomy with slug 'a-taxonomy-that-does-not-exist' does not exist."
