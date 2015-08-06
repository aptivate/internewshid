from __future__ import unicode_literals, absolute_import

import pytest

from ..models import Taxonomy


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
