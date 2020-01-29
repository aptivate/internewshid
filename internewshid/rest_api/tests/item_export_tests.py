import csv
from io import StringIO

from django.urls import reverse

import pytest
from rest_framework.test import APIClient

from data_layer.tests.factories import ItemFactory
from taxonomies.tests.factories import TaxonomyFactory, TermFactory


@pytest.fixture
def client(django_user_model):
    client = APIClient()
    admin = django_user_model.objects.create(is_staff=True)
    client.force_login(user=admin)
    return client


def test_item_exporter(client):
    i1, i2, i3 = ItemFactory(), ItemFactory(), ItemFactory()

    response = client.get(reverse('item-export'))

    assert 'item-export.csv' in response.serialize_headers()
    assert response.accepted_media_type == 'text/csv'

    reader = csv.DictReader(StringIO(response.content))

    assert set(reader.fieldnames) == set([
        'row',
        'age',
        'body',
        'enumerator',
        'external_id',
        'gender',
        'location',
        'sub_location',
        'network_provider',
        'collection_type',
        'terms',
        'timestamp',
        'translation',
    ])


def test_item_terms_exported(client):
    item = ItemFactory()

    tags = TaxonomyFactory(name='Tags')
    categories = TaxonomyFactory(name='Categories')

    trans_ok = TermFactory(taxonomy=tags, name='Translation OK')
    block_c8 = TermFactory(taxonomy=tags, name='Block C8')
    burma = TermFactory(taxonomy=tags, name='Burma')
    wash = TermFactory(taxonomy=categories, name='WASH')
    gbv = TermFactory(taxonomy=categories, name='GBV')

    item.terms.set([trans_ok, block_c8, burma, wash, gbv])
    response = client.get(reverse('item-export'))

    assert 'item-export.csv' in response.serialize_headers()
    assert response.accepted_media_type == 'text/csv'

    reader = csv.DictReader(StringIO(response.content))

    row = next(reader)

    assert row['terms'] == '[Translation OK, Block C8, Burma, WASH, GBV]'
