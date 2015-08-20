from __future__ import unicode_literals, absolute_import
import pytest
from rest_framework.test import APIRequestFactory
from data_layer.tests.factories import ItemFactory
from taxonomies.tests.factories import TermFactory

from ..views import ItemViewSet

from .item_create_view_tests import create_item
from .taxonomy_and_term_create_tests import create_category, add_term
from .categorize_items_tests import categorize_item


def get(data=None):
    view = ItemViewSet.as_view(actions={'get': 'list'})
    request = APIRequestFactory().get('/', data)
    return view(request)


@pytest.mark.django_db
def test_get_items_returns_empty_if_no_items():
    response = get()

    assert response.data == []


@pytest.mark.django_db
def test_get_items_returns_all_items():
    create_item(body='test')

    items = get().data

    assert len(items) == 1
    [item] = items
    assert item['body'] == 'test'


@pytest.mark.django_db
def test_filter_by_body():
    create_item(body="one")
    create_item(body="two")

    payload = get(data={'body': 'one'}).data

    assert len(payload) == 1
    assert payload[0]['body'] == "one"


@pytest.mark.django_db
def test_filter_by_id_list():
    create_item(body='initial item')

    item_ids = []
    for i in range(10):
        item = create_item(body='item %d' % i).data
        item_ids.append(item['id'])

    payload = get(data={'ids': item_ids}).data

    assert len(payload) == 10


@pytest.mark.django_db
def test_filter_by_term():
    taxonomy = create_category(name='taxonomy').data
    term = add_term(taxonomy=taxonomy['slug'], name='term').data
    items = [create_item(body='item %d' % i).data for i in range(3)]

    # Only the first item is categorized
    categorize_item(items[0], term)

    term_filter = '{}:{}'.format(taxonomy['slug'], term['name'])
    payload = get(data={'terms': [term_filter]}).data

    assert len(payload) == 1
    assert payload[0]['body'] == items[0]['body']


@pytest.mark.django_db
def test_filter_by_multiple_terms():
    # TODO: Refactor to use the REST API when we can add
    # multiple terms to an item
    items = [ItemFactory() for i in range(3)]
    terms = [TermFactory() for i in range(3)]

    # All items are categorized with terms[0], only
    # one item is categorized with terms[1]
    for item in items:
        item.terms.add(terms[0])
    items[0].terms.add(terms[1])

    term_filter = [
        '{}:{}'.format(terms[0].taxonomy.slug, terms[0].name),
        '{}:{}'.format(terms[1].taxonomy.slug, terms[1].name)
    ]
    payload = get(data={'terms': term_filter}).data

    assert len(payload) == 1
    assert payload[0]['body'] == items[0].body


@pytest.mark.django_db
def test_filter_by_term_works_when_term_name_includes_colon():
    taxonomy = create_category(name='taxonomy').data
    term = add_term(taxonomy=taxonomy['slug'], name='term:with:colon').data
    item = create_item(body='item 1').data
    categorize_item(item, term)

    term_filter = '{}:{}'.format(taxonomy['slug'], term['name'])
    payload = get(data={'terms': [term_filter]}).data

    assert len(payload) == 1
    assert payload[0]['body'] == item['body']


@pytest.mark.django_db
def test_item_listed_with_associated_terms():
    # TODO: Refactor to use the REST API when we can add
    # multiple terms to an item
    item = ItemFactory()
    terms = [TermFactory() for i in range(3)]
    for term in terms:
        item.terms.add(term)

    [api_item] = get().data
    nested_terms = api_item['terms']

    assert len(nested_terms) == 3
    term_names = [term.name for term in terms]
    assert all(t['name'] in term_names for t in nested_terms)
