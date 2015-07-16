from __future__ import unicode_literals, absolute_import
import pytest

from data_layer.models import Item

from taxonomies.tests.factories import (
    TaxonomyFactory,
    TermFactory)
from transport import items


@pytest.mark.django_db
def test_terms_can_be_added_to_item():
    item = {'body': "What is the cuse of ebola?"}

    response = items.create(item)
    item_id = response['id']

    # TODO: Replace with Term list() ?
    item = Item.objects.get(pk=item_id)
    assert item.terms.count() == 0

    ebola_questions = TaxonomyFactory(name="Ebola Questions")
    term = TermFactory(name="Cause", taxonomy=ebola_questions)
    items.add_term(item_id, ebola_questions.slug, term.name)

    term = TermFactory(name="Question", taxonomy=ebola_questions)
    items.add_term(item_id, ebola_questions.slug, term.name)

    assert item.terms.count() == 2
