from __future__ import absolute_import, unicode_literals

import pytest

import transport
from taxonomies.tests.factories import TaxonomyFactory


@pytest.mark.django_db
def test_list_taxonomies_returns_taxonomies():
    taxonomy = TaxonomyFactory(name="Ebola Questions")

    taxonomies = transport.taxonomies.list()

    names = [t['name'] for t in taxonomies]

    assert taxonomy.name in names
