from __future__ import absolute_import, unicode_literals

import pytest

import transport
from taxonomies.tests.factories import TaxonomyFactory, TermFactory


@pytest.mark.django_db
def test_list_terms_returns_terms():
    taxonomy = TaxonomyFactory(name='A test taxonomy')
    term = TermFactory(name="A test term", taxonomy=taxonomy)

    terms = transport.terms.list()
    terms_as_items = [t.items() for t in terms]

    expected = {
        'taxonomy': taxonomy.slug,
        'name': term.name,
        'long_name': term.long_name
    }.items()

    assert expected in terms_as_items


@pytest.mark.django_db
def test_list_terms_applies_taxonomy_filter():
    taxonomy = TaxonomyFactory(name='A test taxonomy')
    term = TermFactory(name="A test term", taxonomy=taxonomy)
    term_2 = TermFactory(name="A second test term", taxonomy=taxonomy)
    taxonomy_2 = TaxonomyFactory(name='Another test taxonomy')
    TermFactory(name="A third test term", taxonomy=taxonomy_2)

    terms = transport.terms.list(taxonomy=taxonomy.slug)
    terms_as_items = [t.items() for t in terms]

    expected = [t.items() for t in [
        {
            'taxonomy': taxonomy.slug,
            'name': term.name,
            'long_name': term.long_name
        },
        {
            'taxonomy': taxonomy.slug,
            'name': term_2.name,
            'long_name': term_2.long_name
        }

    ]]

    assert len(terms) == 2
    assert sorted(terms_as_items) == sorted(expected)


@pytest.mark.django_db
def test_list_terms_applies_name_filter_accross_taxonomies():
    taxonomy = TaxonomyFactory(name='A test taxonomy')
    term = TermFactory(name="A test term", taxonomy=taxonomy)
    TermFactory(name="Another test term", taxonomy=taxonomy)
    taxonomy_2 = TaxonomyFactory(name='Another test taxonomy')
    term_2 = TermFactory(name="A test term", taxonomy=taxonomy_2)

    terms = transport.terms.list(name="A test term")
    terms_as_items = [t.items() for t in terms]

    expected = [t.items() for t in [
        {
            'taxonomy': taxonomy.slug,
            'name': term.name,
            'long_name': term.long_name
        },
        {
            'taxonomy': taxonomy_2.slug,
            'name': term_2.name,
            'long_name': term_2.long_name
        }
    ]]

    assert len(terms) == 2
    assert sorted(terms_as_items) == sorted(expected)
