import csv
from StringIO import StringIO

from django.urls import reverse

import pytest
from rest_framework.test import APIClient

from data_layer.tests.factories import ItemFactory


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
        'gender',
        'location',
        'network_provider',
        'source',
        'terms',
        'timestamp',
        'translation',
    ])
