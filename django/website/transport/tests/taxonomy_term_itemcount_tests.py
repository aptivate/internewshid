from __future__ import unicode_literals, absolute_import
import pytest

from taxonomies.tests.factories import (
    TaxonomyFactory,
    TermFactory,
)

import transport


@pytest.fixture
def item_data():
    item = {'body': "What is the cuse of ebola?"}
    return transport.items.create(item)


@pytest.fixture
def questions_category():
    # TODO: Replace with transport call when we have one
    return TaxonomyFactory(name="Ebola Questions")


@pytest.fixture
def questions_term(questions_category):
    # TODO: Replace with transport call when we have one
    return TermFactory(taxonomy=questions_category)


@pytest.mark.django_db
def test_term_itemcount_returns_terms_and_counts(item_data,
                                                 questions_category,
                                                 questions_term):

    # This is tested more comprehensively in the API tests
    transport.items.add_term(item_data['id'],
                             questions_category.slug,
                             questions_term.name)

    terms = transport.taxonomies.term_itemcount(slug=questions_category.slug)
    counts = {term['name']: term['count'] for term in terms}

    assert counts[questions_term.name] == 1
