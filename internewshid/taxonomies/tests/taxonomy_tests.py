import pytest

from ..models import Taxonomy
from .factories import TaxonomyFactory


@pytest.mark.django_db
def test_taxonomies_have_a_slug():
    taxonomy = Taxonomy(name="Test Taxonomy")

    taxonomy.save()

    assert taxonomy.slug == "test-taxonomy"


@pytest.mark.django_db
def test_taxonomies_cannot_have_colon_in_slug():
    """ It is important for the rest API item search
        that taxonomy slugs do not contain colons
        (so query parameters can be formated as
         <taxonomy slug>:<term name>).

        This test is added here to prevent regression.
    """
    # Ensure colons are stripped when doing automatic
    # slugs
    taxonomy1 = Taxonomy(name="A taxonony with : colons")
    taxonomy1.save()

    assert ':' not in taxonomy1.slug

    # Ensure attempting to force a colon in a slug fails
    taxonomy2 = Taxonomy(name="A taxonomy with defined slug",
                         slug="a-slug-with:colon")
    taxonomy2.save()

    assert ':' not in taxonomy2.slug


@pytest.mark.django_db
def test_is_optional_true_for_multiplicity_optional():
    taxonomy = TaxonomyFactory(multiplicity='optional')

    assert taxonomy.is_optional


@pytest.mark.django_db
def test_is_optional_false_for_multiplicity_multiple():
    taxonomy = TaxonomyFactory(multiplicity='multiple')

    assert not taxonomy.is_optional


@pytest.mark.django_db
def test_is_multiple_false_for_multiplicity_optional():
    taxonomy = TaxonomyFactory(multiplicity='optional')

    assert not taxonomy.is_multiple


@pytest.mark.django_db
def test_is_multiple_true_for_multiplicity_multiple():
    taxonomy = TaxonomyFactory(multiplicity='multiple')

    assert taxonomy.is_multiple


@pytest.mark.django_db
def test_is_open_true_for_vocabulary_open():
    taxonomy = TaxonomyFactory(vocabulary='open')

    assert taxonomy.is_open


@pytest.mark.django_db
def test_is_open_false_for_vocabulary_fixed():
    taxonomy = TaxonomyFactory(vocabulary='fixed')

    assert not taxonomy.is_open


@pytest.mark.django_db
def test_is_open_false_for_vocabulary_closed():
    taxonomy = TaxonomyFactory(vocabulary='closed')

    assert not taxonomy.is_open
