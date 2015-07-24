from __future__ import unicode_literals, absolute_import
import pytest

from taxonomies.tests.factories import TaxonomyFactory
import transport


@pytest.mark.django_db
def test_list_taxonomies_returns_taxonomies():
    taxonomy = TaxonomyFactory(name="Ebola Questions")

    taxonomies = transport.taxonomies.list()

    assert len(taxonomies) == 1
    [taxonomy] = taxonomies
    assert taxonomy['name'] == 'Ebola Questions'
