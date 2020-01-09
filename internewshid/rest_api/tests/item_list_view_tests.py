from __future__ import absolute_import, unicode_literals

import pytest
from rest_framework.test import APIRequestFactory

from data_layer.tests.factories import ItemFactory
from taxonomies.tests.factories import TermFactory

from ..views import ItemViewSet
from .categorize_items_tests import categorize_item
from .item_create_view_tests import create_item
from .taxonomy_and_term_create_tests import add_term, create_taxonomy


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
    taxonomy = create_taxonomy(name='taxonomy').data
    term = add_term(taxonomy=taxonomy['slug'], name='term').data
    items = [create_item(body='item %d' % i).data for i in range(3)]

    # Only the first item is categorized
    categorize_item(items[0], term)

    term_filter = '{}:{}'.format(taxonomy['slug'], term['name'])
    payload = get(data={'terms': [term_filter]}).data

    assert len(payload) == 1
    assert payload[0]['body'] == items[0]['body']


@pytest.mark.django_db
def test_filter_by_date_range():
    create_item(
        body="Too old item",
        timestamp='2018-10-25 23:59:59+0000'
    )

    create_item(
        body="In range item 1",
        timestamp='2018-10-26 00:00:00+0000'
    )

    create_item(
        body="In range item 2",
        timestamp='2018-10-27 00:00:00+0000'
    )

    create_item(
        body="Too new item",
        timestamp='2018-10-27 00:00:01+0000'
    )

    payload = get(data={
        'start_time': '2018-10-26 00:00:00+0000',
        'end_time': '2018-10-27 00:00:00+0000'
    }).data

    assert len(payload) == 2

    # default ordering is timestamp desc
    assert payload[0]['body'] == "In range item 2"
    assert payload[1]['body'] == "In range item 1"


@pytest.mark.django_db
def test_filter_by_age_range():
    create_item(
        body="Too old item",
        age='38'
    )

    create_item(
        body="In range item 1",
        age='34'
    )

    create_item(
        body="In range item 2",
        age='37'
    )

    create_item(
        body="Too young item",
        age='33'
    )

    payload = get(data={
        'from_age': '34',
        'to_age': '37',
        'ordering': 'body',
    }).data

    assert len(payload) == 2
    assert payload[0]['body'] == "In range item 1"
    assert payload[1]['body'] == "In range item 2"


@pytest.mark.django_db
def test_filter_by_location():
    create_item(body='item1', location='foo')
    create_item(body='neo', location='somewhere')
    create_item(body='item2', location='bar')

    payload = get(data={'location': 'somewhere'}).data

    assert len(payload) == 1
    assert payload[0]['body'] == 'neo'
    assert payload[0]['location'] == 'somewhere'


@pytest.mark.django_db
def test_filter_by_enumerator():
    create_item(
        body='item1',
        enumerator='Yasmin')
    create_item(
        body='item2',
        enumerator='Collected by ....Mohammed yousuf@ Mohammed Ullah'
    )

    payload = get(
        data={
            'enumerator': 'Collected by ....Mohammed yousuf@ Mohammed Ullah',
        }
    ).data

    assert len(payload) == 1
    assert payload[0]['body'] == 'item2'


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
    taxonomy = create_taxonomy(name='taxonomy').data
    term = add_term(taxonomy=taxonomy['slug'], name='term:with:colon').data
    item = create_item(body='item 1').data
    categorize_item(item, term)

    term_filter = '{}:{}'.format(taxonomy['slug'], term['name'])
    payload = get(data={'terms': [term_filter]}).data

    assert len(payload) == 1
    assert payload[0]['body'] == item['body']


@pytest.mark.django_db
def test_empty_term_filter_ignored():
    taxonomy = create_taxonomy(name='taxonomy').data
    term = add_term(taxonomy=taxonomy['slug'], name='my term').data
    item1 = create_item(body='item 1').data
    item2 = create_item(body='item 2').data
    categorize_item(item1, term)

    term_filter = '{}:'.format(taxonomy['slug'])
    payload = get(
        data={
            'terms': [term_filter],
            'ordering': 'body',
            }
    ).data

    assert len(payload) == 2
    assert payload[0]['body'] == item1['body']
    assert payload[1]['body'] == item2['body']


@pytest.mark.django_db
def test_items_filtered_by_one_term_or_another():
    items = [ItemFactory() for i in range(4)]
    terms = [TermFactory() for i in range(2)]

    items[1].terms.add(terms[0])
    items[2].terms.add(terms[1])
    items[3].terms.add(terms[0])
    items[3].terms.add(terms[1])

    term_filter = [
        '{}:{}'.format(terms[0].taxonomy.slug, terms[0].name),
        '{}:{}'.format(terms[1].taxonomy.slug, terms[1].name)
    ]
    results = get(data={'terms_or': term_filter}).data

    ids = [r['id'] for r in results]

    assert items[0].id not in ids
    assert items[1].id in ids
    assert items[2].id in ids
    assert items[3].id in ids


@pytest.mark.django_db
def test_filter_by_external_id_fragment():
    create_item(
        body='Matching 1',
        external_id='08a28ec8-0c27-4cc7-9e2c-c27e04a28787')
    create_item(
        body='Matching 2',
        external_id='932e3597-247d-4cc7-b16a-05d3a71c6d9c'
    )
    create_item(
        body='Not matching',
        external_id='d1ddf585-9d0e-4b64-bc6f-e4c30a24c3c0'
    )

    payload = get(
        data={
            'external_id_pattern': '4cc7',
        }
    ).data

    assert len(payload) == 2
    assert payload[0]['body'] == 'Matching 1'
    assert payload[1]['body'] == 'Matching 2'


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


@pytest.mark.django_db
def test_ordering_by_default_is_timestamp_desc():
    create_item(
        body="item 1",
        timestamp='2018-10-25 23:59:59+0000'
    )

    create_item(
        body="item 2",
        timestamp='2018-10-26 00:00:00+0000'
    )

    create_item(
        body="item 3",
        timestamp='2018-10-27 00:00:00+0000'
    )

    create_item(
        body="item 4",
        timestamp='2018-10-27 00:00:01+0000'
    )

    payload = get(data={}).data

    assert payload[0]['body'] == "item 4"
    assert payload[1]['body'] == "item 3"
    assert payload[2]['body'] == "item 2"
    assert payload[3]['body'] == "item 1"


@pytest.mark.django_db
def test_ordering_by_body():
    create_item(
        body="item 1",
        timestamp='2018-10-25 23:59:59+0000'
    )

    create_item(
        body="item 2",
        timestamp='2018-10-26 00:00:00+0000'
    )

    create_item(
        body="item 3",
        timestamp='2018-10-27 00:00:00+0000'
    )

    create_item(
        body="item 4",
        timestamp='2018-10-27 00:00:01+0000'
    )

    payload = get(data={'ordering': 'body'}).data

    assert payload[0]['body'] == "item 1"
    assert payload[1]['body'] == "item 2"
    assert payload[2]['body'] == "item 3"
    assert payload[3]['body'] == "item 4"


@pytest.mark.django_db
def test_filter_message_by_keyword():
    create_item(
        body="""Latrine ipsum dolor sit amet, consectetur adipiscing elit.
Pellentesque vitae ipsum a magna rutrum facilisis. Fusce vitae dolor dolor.
Nullam."""
    )

    create_item(
        body="""Lorem ipsum dolor sit amet, consectetur adipiscing elit.
Suspendisse ut orci diam. Donec scelerisque id massa vitae laoreet. Ut sit."""
    )

    create_item(
        body="""Lorem ipsum dolor sit amet, consectetur adipiscing elit.
Pellentesque ac orci felis. Pellentesque hendrerit laoreet dolor nec euismod.
 Fusce pretium."""
    )

    create_item(
        body="""Lorem ipsum dolor sit amet, consectetur adipiscing elit.
 Donec at justo sit amet ante LATRINE semper tempus. Suspendisse vulputate
 urna nec."""
    )

    create_item(
        body="""Lorem ipsum dolor sit amet, consectetur adipiscing elit.
Mauris nec mauris vestibulum, laoreet mi ut, facilisis massa. Pellentesque
 quam tortor. latrines"""
    )

    payload = get(
        data={
            'search': 'latrine',
            'ordering': 'body',
        }
    ).data

    assert len(payload) == 3

    assert 'Latrine' in payload[0]['body']
    assert 'LATRINE' in payload[1]['body']
    assert 'latrines' in payload[2]['body']


@pytest.mark.django_db
def test_filter_translation_by_keyword():
    create_item(
        body="item 1",
        translation="""Latrine ipsum dolor sit amet, consectetur adipiscing elit.
Pellentesque vitae ipsum a magna rutrum facilisis. Fusce vitae dolor dolor.
Nullam."""
    )

    create_item(
        body="item 2",
        translation="""Lorem ipsum dolor sit amet, consectetur adipiscing elit.
Suspendisse ut orci diam. Donec scelerisque id massa vitae laoreet. Ut sit."""
    )

    create_item(
        body="item 3",
        translation="""Lorem ipsum dolor sit amet, consectetur adipiscing elit.
Pellentesque ac orci felis. Pellentesque hendrerit laoreet dolor nec euismod.
 Fusce pretium."""
    )

    create_item(
        body="item 4",
        translation="""Lorem ipsum dolor sit amet, consectetur adipiscing elit.
 Donec at justo sit amet ante LATRINE semper tempus. Suspendisse vulputate
 urna nec."""
    )

    create_item(
        body="item 5",
        translation="""Lorem ipsum dolor sit amet, consectetur adipiscing elit.
        Mauris nec mauris vestibulum, laoreet mi ut, facilisis massa.
        Pellentesque quam tortor. latrines""",
    )

    payload = get(
        data={
            'search': 'latrine',
            'ordering': 'body',
        }
    ).data

    assert len(payload) == 3

    assert 'Latrine' in payload[0]['translation']
    assert 'LATRINE' in payload[1]['translation']
    assert 'latrines' in payload[2]['translation']


@pytest.mark.django_db
def test_filtering_a_message_must_match_all_keywords():
    item_1 = create_item(
        body="""Latrine ipsum dolor sit amet, consectetur adipiscing elit.
Pellentesque vitae ipsum a magna rutrum facilisis. Fusce vitae dolor dolor.
Nullam."""
    )

    create_item(
        body="""Lorem ipsum dolor sit amet, latrine consectetur adipiscing elit.
Suspendisse ut orci diam. Donec scelerisque id massa vitae laoreet. Ut sit."""
    )

    create_item(
        body="""Lorem ipsum dolor sit amet, magna consectetur adipiscing elit.
Pellentesque ac orci felis. Pellentesque hendrerit laoreet dolor nec euismod.
 Fusce pretium."""
    )

    payload = get(
        data={
            'search': 'latrine magna',
        }
    ).data

    assert len(payload) == 1

    assert payload[0]['body'] == item_1.data['body']


@pytest.mark.django_db
def test_filtering_a_translation_must_match_all_keywords():
    item_1 = create_item(
        body="item 1",
        translation="""Latrine ipsum dolor sit amet, consectetur adipiscing elit.
Pellentesque vitae ipsum a magna rutrum facilisis. Fusce vitae dolor dolor.
Nullam."""
    )

    create_item(
        body="item 2",
        translation="""Lorem ipsum dolor sit amet, latrine consectetur adipiscing elit.
Suspendisse ut orci diam. Donec scelerisque id massa vitae laoreet. Ut sit."""
    )

    create_item(
        body="item 3",
        translation="""Lorem ipsum dolor sit amet, magna consectetur adipiscing elit.
Pellentesque ac orci felis. Pellentesque hendrerit laoreet dolor nec euismod.
 Fusce pretium."""
    )

    payload = get(
        data={
            'search': 'latrine magna',
        }
    ).data

    assert len(payload) == 1

    assert payload[0]['body'] == "item 1"
