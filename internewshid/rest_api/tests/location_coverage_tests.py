import csv
from StringIO import StringIO

from django.urls import reverse
from django.utils import timezone

import pytest
from rest_framework.test import APIClient

from data_layer.models import Item
from taxonomies.models import Taxonomy, Term


@pytest.fixture
def client(django_user_model):
    client = APIClient()
    admin = django_user_model.objects.create(is_staff=True)
    client.force_login(user=admin)
    return client


def test_location_coverage_unauthenticated():
    response = APIClient().get(reverse('location-coverage'))
    assert response.status_code == 403


def test_location_coverage(client):
    NOW = timezone.now().replace(microsecond=0)

    taxonomy = Taxonomy.objects.create(name='topicbaz')
    item1 = Item.objects.create(location='locationfoo', timestamp=NOW)

    term = Term.objects.create(taxonomy=taxonomy, name='termbar')
    item1.terms.add(term)
    item1.save()

    Item.objects.create()

    response = client.get(reverse('location-coverage'))

    assert 'location-coverage.csv' in response.serialize_headers()
    assert response.accepted_media_type == 'text/csv'

    reader = csv.DictReader(StringIO(response.content))

    assert reader.fieldnames == ['row', 'location', 'terms', 'timestamp']

    rendered = [item for item in reader]

    assert rendered[0]['location'] == 'locationfoo'
    assert rendered[0]['terms'] == '[termbar]'

    assert rendered[1]['location'] == ''
    assert rendered[1]['terms'] == '[]'
