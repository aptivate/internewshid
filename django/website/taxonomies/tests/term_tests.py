from __future__ import unicode_literals, absolute_import

import pytest

from ..models import Term
from .factories import TermFactory, TaxonomyFactory



@pytest.fixture
def term_with_context():
    tax = TaxonomyFactory()  # known taxonomy
    _ = TermFactory(name="name")  # term with same name in different taxonomy
    _ = TermFactory(taxonomy=tax) # another different term in the sam taxonomy
    return TermFactory(taxonomy=tax, name="name")


@pytest.mark.django_db
def test_term_by_taxonomy_with_taxonomies_with_slug(term_with_context):
    term = Term.objects.by_taxonomy(
        taxonomy=term_with_context.taxonomy.slug,
        name=term_with_context.name,
    )

    assert term.name == term_with_context.name
    assert term.taxonomy == term_with_context.taxonomy


@pytest.mark.django_db
def test_term_by_taxonomy_with_taxonomies_with_taxonomy(term_with_context):
    term = Term.objects.by_taxonomy(
        taxonomy=term_with_context.taxonomy,
        name=term_with_context.name,
    )

    assert term.name == term_with_context.name
    assert term.taxonomy == term_with_context.taxonomy
