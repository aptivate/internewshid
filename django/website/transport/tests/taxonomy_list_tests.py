from __future__ import unicode_literals, absolute_import
import pytest

from taxonomies.tests.factories import TaxonomyFactory
import transport


@pytest.mark.django_db
def test_list_taxonomies_returns_taxonomies():
    taxonomy = TaxonomyFactory(name="Ebola Questions")

    taxonomies = transport.taxonomies.list()

    names = [t['name'] for t in taxonomies]

    assert taxonomy.name in names
