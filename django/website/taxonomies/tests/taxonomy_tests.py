from __future__ import unicode_literals, absolute_import

import pytest

from ..models import Taxonomy


@pytest.mark.django_db
def test_taxonomies_have_a_slug():
    taxonomy = Taxonomy(name="Test Taxonomy")

    taxonomy.save()

    assert taxonomy.slug == "test-taxonomy"
