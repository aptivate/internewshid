import datetime

import pytest
from rest_framework import status
from rest_framework.test import APIRequestFactory

from ..views import ItemViewSet, TaxonomyViewSet, TermViewSet


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


def create_taxonomy(**kwargs):
    request = APIRequestFactory().put("", kwargs)
    view = TaxonomyViewSet.as_view(actions={'put': 'create'})

    response = view(request)
    assert status.is_success(response.status_code), response.data

    return response


def term_for(taxonomy, name):
    """ Create, and return a Term in the given taxonomy """
    response = add_term(
        taxonomy=taxonomy['slug'],
        name=name,
    )
    assert status.is_success(response.status_code), response.data

    return response.data


@pytest.fixture
def category():
    response = create_taxonomy(name="Test Ebola Questions")
    assert status.is_success(response.status_code), response.data

    return response.data


@pytest.fixture
def vaccine_term():
    category = create_taxonomy(name="Test Ebola Questions").data

    return term_for(category, 'Vaccine')


@pytest.fixture
def timescales_term(category):
    return term_for(category, 'Timescales')


@pytest.fixture
def monrovia_term():
    category = create_taxonomy(name="Test Regions").data

    return term_for(category, 'Vaccine')
