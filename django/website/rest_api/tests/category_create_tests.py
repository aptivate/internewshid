from __future__ import unicode_literals, absolute_import

import pytest

from django.core.urlresolvers import reverse
from rest_framework.test import APIRequestFactory

from data_layer.models import Taxonomy
from ..views import TaxonomyViewSet


def create_category(name):
    url = reverse('category-list')
    request = APIRequestFactory().put(url, {'name': name})
    view = TaxonomyViewSet.as_view(actions={'put': 'create'})
    return view(request, pk=id)


def test_create_a_category():

    create_category('Animal')

    assert Taxonomy.objects.count() == 1
    [taxonomy] = Taxonomy.objects.all()
    assert taxonomy.name == 'Animal'
