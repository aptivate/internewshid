from __future__ import absolute_import, unicode_literals

import pytest

from ..models import Term
from .factories import TaxonomyFactory, TermFactory


@pytest.fixture
def term_with_context():
    tax = TaxonomyFactory()  # known taxonomy
    _ = TermFactory(name="name")  # term with same name in different taxonomy
    _ = TermFactory(taxonomy=tax)  # another different term in the sam taxonomy
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


@pytest.mark.django_db
def test_unknown_term_by_taxonomy_creates_term_if_open():
    taxonomy = TaxonomyFactory(vocabulary='open')

    term = Term.objects.by_taxonomy(
        taxonomy=taxonomy,
        name="a term that doesn't exist",
    )

    assert term.name == "a term that doesn't exist"
    assert term.taxonomy == taxonomy


@pytest.mark.django_db
def test_unknown_term_by_taxonomy_throws_exception_if_not_open():
    taxonomy = TaxonomyFactory(vocabulary='closed')

    with pytest.raises(Term.DoesNotExist) as excinfo:
        Term.objects.by_taxonomy(
            taxonomy=taxonomy,
            name="a term that doesn't exist",
        )

    assert excinfo.value.message == "Term matching query does not exist."
