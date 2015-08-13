from __future__ import unicode_literals, absolute_import
import pytest

from rest_framework.test import APIRequestFactory
from rest_framework import status

from rest_api.views import ItemViewSet

from .categorize_items_tests import (
    term_for,
    categorize_item,
)
from .item_create_view_tests import create_item
from .item_list_view_tests import get as list_items
from .taxonomy_and_term_create_tests import (
    create_category,
)


def update_item(id, **kwargs):
    url = '/items/%d' % id  # Not used as we call the view directly
    request = APIRequestFactory().put(url, kwargs)
    view = ItemViewSet.as_view(actions={'put': 'update'})

    response = view(request, pk=id)
    assert status.is_success(response.status_code), response.data

    return response


@pytest.mark.django_db
def test_item_fields_can_be_updated():
    old_data = {'body': 'That the government is using this Ebola as a business to inrich few governmemt official',
                'network_provider': '8737 (Lonestar)'}
    new_data = {'body': 'That the government is using this Ebola as a business to inrich few government official',
                'network_provider': '8737 (CellCom)'}

    response = create_item(**old_data)
    id = response.data['id']

    update_item(id, **new_data)

    [item] = list_items().data

    assert item['body'] == new_data['body']
    assert item['network_provider'] == new_data['network_provider']


@pytest.mark.django_db
def test_item_terms_not_affected_by_update():
    item = create_item(body='What is the cuse of Ebola?').data
    id = item['id']

    questions_category = create_category("Test Ebola Questions").data

    categorize_item(item, term_for(questions_category, 'Vaccine'))

    [item] = list_items().data
    terms = item['terms']
    assert len(terms) == 1

    update_item(id, body='s')

    [item] = list_items().data
    terms = item['terms']
    assert len(terms) == 1


@pytest.mark.django_db
@pytest.mark.xfail
def test_item_terms_can_be_updated():
    item = create_item(body='What is the cuse of Ebola?').data
    id = item['id']

    questions_category = create_category("Test Ebola Questions").data
    regions_category = create_category("Test Regions").data
    types_category = create_category("Test Item Types").data

    categorize_item(item, term_for(questions_category, 'Vaccine'))
    categorize_item(item, term_for(regions_category, 'Monrovia'))

    [item] = list_items().data
    terms = item['terms']
    assert len(terms) == 2

    new_terms = [{'taxonomy': questions_category['slug'],
                  'name': 'Vaccine'},
                 {'taxonomy': types_category['slug'],
                  'name': 'Question'}]

    update_item(id, terms=new_terms, body='s')

    [item] = list_items().data
    terms = item['terms']
    assert len(terms) == 2

    names = [t['name'] for t in terms]

    assert 'Vaccine' in names
    assert 'Question' in names
    assert 'Monrovia' not in names

# TODO: Test timestamp updated
# TODO: Test error when new term doesn't exist
