import pytest

from .factories import ItemFactory
from taxonomies.tests.factories import TermFactory, TaxonomyFactory


@pytest.mark.django_db
def test_apply_term_replaces_term_for_categories():
    item = ItemFactory()
    taxonomy = TaxonomyFactory()  # Ensure multiplicity = optional
    term1 = TermFactory(taxonomy=taxonomy)
    term2 = TermFactory(taxonomy=taxonomy)
    assert taxonomy.is_optional

    item.apply_term(term1)
    assert list(item.terms.all()) == [term1]

    item.apply_term(term2)
    assert list(item.terms.all()) == [term2]

@pytest.mark.xfail
# I'm putting this here to explain some of my thinking.
@pytest.mark.django_db
def test_apply_term_adds_term_for_tags():
    item = ItemFactory()
    taxonomy = TaxonomyFactory()  # Ensure multiplicity == multiple
    term1 = TermFactory(taxonomy=taxonomy)
    term2 = TermFactory(taxonomy=taxonomy)
    assert taxonomy.is_multiple

    item.apply_term(term1)
    assert list(item.terms.all()) == [term1]

    item.apply_term(term2)
    assert set(item.terms.all()) == set([term1, term2])
