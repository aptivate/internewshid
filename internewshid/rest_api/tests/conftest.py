import datetime

import pytest
from rest_framework import status
from rest_framework.test import APIRequestFactory

from taxonomies.tests.factories import TaxonomyFactory

from ..views import ItemViewSet, TermViewSet


def create_item(**kwargs):
    if 'timestamp' not in kwargs:
        kwargs['timestamp'] = datetime.datetime.now()

    request = APIRequestFactory().post('/items', kwargs)
    view = ItemViewSet.as_view(actions={'post': 'create'})
    response = view(request)
    assert status.is_success(response.status_code), response.data

    return response


@pytest.fixture
def item():
    return create_item(body="Text").data


def add_term(**kwargs):
    """
        taxonomy: string with taxonomy name
        term: name of term
    """
    request = APIRequestFactory().post("", kwargs)
    view = TermViewSet.as_view(actions={'post': 'create'})
    response = view(request)
    assert status.is_success(response.status_code), response.data

    return response


def term_for(taxonomy, name):
    """ Create, and return a Term in the given taxonomy """
    response = add_term(
        taxonomy=taxonomy.slug,
        name=name,
    )
    assert status.is_success(response.status_code), response.data

    return response.data


@pytest.fixture
def category():
    taxonomy = TaxonomyFactory(name="Test Ebola Questions")

    return taxonomy


@pytest.fixture
def vaccine_term():
    category = TaxonomyFactory(name="Test Ebola Questions")

    return term_for(category, 'Vaccine')


@pytest.fixture
def timescales_term(category):
    return term_for(category, 'Timescales')


@pytest.fixture
def monrovia_term():
    category = TaxonomyFactory(name="Test Regions")

    return term_for(category, 'Vaccine')
