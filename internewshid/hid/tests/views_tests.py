from django.contrib.messages.storage.fallback import FallbackStorage
from django.http import HttpResponseRedirect, QueryDict
from django.test import RequestFactory
from django.urls import reverse

import pytest
from mock import Mock

import transport
from hid.constants import ITEM_TYPE_CATEGORY
from hid.tabs.view_and_edit_table import (
    DELETE_COMMAND, REMOVE_QTYPE_COMMAND, ViewAndEditTableTab, _delete_items,
    _get_view_and_edit_form_request_parameters,
    view_and_edit_table_form_process_items
)
from tabbed_page.tests.factories import TabbedPageFactory, TabInstanceFactory
from taxonomies.models import Taxonomy, Term
from taxonomies.tests.factories import TaxonomyFactory, TermFactory

ReqFactory = RequestFactory()


@pytest.fixture
def item_type_taxonomy():
    slug = ITEM_TYPE_CATEGORY['question']

    try:
        taxonomy = Taxonomy.objects.get(slug=slug)
    except Taxonomy.DoesNotExist:
        taxonomy = Taxonomy.objects.create(name=slug)

    return taxonomy


def fix_messages(request):
    '''
    Save use of messages with RequestFactory.

    Stored message objects can be found in: request._messages._queued_messages
    (attributes: level, level_tag, message, tags)
    '''
    setattr(request, 'session', 'session')
    messages = FallbackStorage(request)
    setattr(request, '_messages', messages)
    return request


def assert_message(request, level, content):
    messages = [(m.message, m.level)
                for m in request._messages._queued_messages]

    assert (content, level) in messages


def assert_no_messages(request, level):
    messages = [m.message
                for m in request._messages._queued_messages if m.level == level]

    assert messages == []


def check_message(request, content):
    for msg in request._messages._queued_messages:
        if msg.message == content:
            return True
    return False


@pytest.fixture
def request_item():
    '''Create item and request'''

    msg = {'body': "Message text"}
    transport.items.create(msg)

    [item] = list(transport.items.list())

    url = reverse('data-view-process')
    request = ReqFactory.post(url, {
        'action': 'batchupdate-top',
        'batchaction-top': DELETE_COMMAND,
        'select_item_id': [item['id']],
        'next': 'http://localhost/testurl'
    })
    request = fix_messages(request)

    return [request, item]


def check_item_was_deleted(request):
    assert check_message(request, u"1 item deleted.") is True

    items = list(transport.items.list())
    assert len(list(items)) == 0


@pytest.mark.django_db
def test_delete_items_deletes_items(request_item):
    req, item = request_item
    _delete_items(req, [item['id']])
    check_item_was_deleted(req)


@pytest.mark.django_db
def test_process_items_deletes_items(request_item):
    req, item = request_item
    view_and_edit_table_form_process_items(req)
    check_item_was_deleted(req)


@pytest.mark.django_db
def test_process_items_removes_question_type(item_type_taxonomy):
    msg = {'body': "Message text"}
    transport.items.create(msg)

    [item] = list(transport.items.list())

    term_to_delete = TermFactory(name='term to be deleted',
                                 taxonomy=item_type_taxonomy)
    transport.items.add_terms(
        item['id'], term_to_delete.taxonomy.slug, term_to_delete.name)

    term_to_keep = TermFactory(name='term not to be deleted')
    transport.items.add_terms(
        item['id'], term_to_keep.taxonomy.slug, term_to_keep.name)

    url = reverse('data-view-process')
    request = ReqFactory.post(url, {
        'action': 'batchupdate-top',
        'batchaction-top': REMOVE_QTYPE_COMMAND,
        'select_item_id': [item['id']],
        'next': 'http://localhost/testurl'
    })

    request = fix_messages(request)
    view_and_edit_table_form_process_items(request)

    [item] = list(transport.items.list())

    term_names = [t['name'] for t in item['terms']]

    assert term_to_keep.name in term_names
    assert term_to_delete.name not in term_names


def test_empty_process_items_redirects_to_data_view():
    url = reverse('data-view-process')
    redirect_url = reverse('tabbed-page', kwargs={
        'name': 'main',
        'tab_name': 'all'
    })

    request = ReqFactory.get(url)

    response = view_and_edit_table_form_process_items(request)
    assert response.url == redirect_url
    assert isinstance(response, HttpResponseRedirect) is True


@pytest.mark.django_db
def test_process_items_redirects_to_provided_url(request_item):
    req, item = request_item
    response = view_and_edit_table_form_process_items(req)
    assert response.url == 'http://localhost/testurl'
    assert isinstance(response, HttpResponseRedirect) is True


@pytest.mark.django_db
def test_get_category_options_uses_terms():
    # TODO: Rewrite tests to use transport layer
    ebola_questions = TaxonomyFactory(name="Ebola Questions")
    other_taxonomy = TaxonomyFactory(name="Should be ignored")
    type_1 = TermFactory(
        name="Measures",
        taxonomy=ebola_questions,
        long_name="What measures could end Ebola?",
    )
    type_2 = TermFactory(
        name="Survivors",
        taxonomy=ebola_questions,
        long_name="Are survivors stigmatized?",
    )
    type_3 = TermFactory(
        name="Victims",
        taxonomy=ebola_questions,
        long_name="Number of Victims?",
    )
    other_term = TermFactory(
        name="Should be ignored",
        taxonomy=other_taxonomy,
    )

    table = ViewAndEditTableTab()
    options = table._get_category_options(categories=[ebola_questions.slug])

    assert (type_1.name, type_1.name) in options
    assert (type_2.name, type_2.name) in options
    assert (type_3.name, type_3.name) in options
    assert (other_term.name, other_term.long_name) not in options


@pytest.mark.django_db
def test_get_category_options_orders_by_lowercase_name():
    # TODO: Rewrite tests to use transport layer
    taxonomy = TaxonomyFactory(name="order_by_lowercase_name_test")
    test_term_values = [
        ('test a1', '1'), ('test b1', '2'),
        ('test A2', '3'), ('test B2', '4')
    ]
    for test_value in test_term_values:
        TermFactory(
            name=test_value[0],
            long_name=test_value[1],
            taxonomy=taxonomy
        )

    table = ViewAndEditTableTab()
    options = table._get_category_options(categories=[taxonomy.slug])

    # Expected is the list ordered by lowercase short name.
    expected = [(short, short) for short, long_name in test_term_values]
    expected = tuple(sorted(expected, key=lambda e: e[0].lower()))

    assert options == expected


@pytest.mark.django_db
def test_actions_includes_remove_question_type_option():
    page = TabbedPageFactory()
    tab_instance = TabInstanceFactory(page=page)
    request = Mock(GET={})
    tab = ViewAndEditTableTab()

    term = TermFactory()
    categories = [term.taxonomy.slug]

    context_data = tab.get_context_data(tab_instance,
                                        request,
                                        categories=categories)

    actions = context_data['actions'][0]
    assert actions['label'] == 'Actions'
    assert 'remove-question-type' in actions['items']


@pytest.mark.django_db
def test_actions_excludes_remove_question_type_option_for_no_categories():
    page = TabbedPageFactory()
    tab_instance = TabInstanceFactory(page=page)
    request = Mock(GET={})
    tab = ViewAndEditTableTab()

    context_data = tab.get_context_data(tab_instance,
                                        request)

    actions = context_data['actions'][0]
    assert actions['label'] == 'Actions'
    assert 'remove-question-type' not in actions['items']


def test_views_item_get_request_parameters_renames_items_of_active_location():
    query = QueryDict(
        'action=something-bottom&item-top=top-value&item-bottom=bottom-value'
    )
    expected = {
        'action': 'something',
        'item': 'bottom-value',
        'item-top': 'top-value'
    }
    actual = _get_view_and_edit_form_request_parameters(query)
    assert actual.dict() == expected


def test_views_item_get_request_parameters_sets_default_location():
    query = QueryDict(
        'action=something&item-top=top-value&item-bottom=bottom-value'
    )
    expected = {
        'action': 'something',
        'item': 'top-value',
        'item-bottom': 'bottom-value'
    }
    actual = _get_view_and_edit_form_request_parameters(query)
    assert actual.dict() == expected


def test_views_item_get_request_parameters_sets_default_action_and_location():
    query = QueryDict(
        'item-top=top-value&item-bottom=bottom-value'
    )
    expected = {
        'action': 'none',
        'item': 'top-value',
        'item-bottom': 'bottom-value'
    }
    actual = _get_view_and_edit_form_request_parameters(query)
    assert actual.dict() == expected


@pytest.mark.django_db
def test_view_and_edit_table_tab_sets_add_button_context():
    item_types = TaxonomyFactory(slug="item-types", name="Item Types")
    test_item_type = TermFactory(
        name='test-item-type',
        taxonomy=item_types,
        long_name="Test Item Type"
    )
    page = TabbedPageFactory()
    tab_instance = TabInstanceFactory(page=page)
    request = Mock(GET={})
    tab = ViewAndEditTableTab()

    filters = {'terms': ['item-types:test-item-type']}
    context_data = tab.get_context_data(
        tab_instance, request, filters=filters
    )

    assert context_data['add_button_for'] == {
        'taxonomy': 'item-types',
        'name': test_item_type.name,
        'long_name': test_item_type.long_name
    }


@pytest.mark.django_db
def test_table_items_filtered_by_item_type_category(item_type_taxonomy):
    wash_item = transport.items.create({
        'body': "Message in WASH category",
    })

    gbv_item = transport.items.create({
        'body': "Message in GBV category",
    })

    transport.items.create({
        'body': "Message in no category",
    })

    wash_term = TermFactory(name='WASH', taxonomy=item_type_taxonomy)
    transport.items.add_terms(
        wash_item['id'], wash_term.taxonomy.slug, wash_term.name)

    gbv_term = TermFactory(name='GBV', taxonomy=item_type_taxonomy)
    transport.items.add_terms(
        gbv_item['id'], gbv_term.taxonomy.slug, gbv_term.name)

    page = TabbedPageFactory()
    tab_instance = TabInstanceFactory(page=page)
    request = Mock(GET={'category': 'WASH'})
    tab = ViewAndEditTableTab()
    context_data = tab.get_context_data(
        tab_instance, request, categories=[item_type_taxonomy.slug],
        dynamic_filters=['category']
    )

    table = context_data['table']

    ids = [t['id'] for t in table.data.data]

    assert ids == [wash_item['id']]


@pytest.mark.django_db
def test_table_items_filtered_by_item_type_category_and_default_filter(
        item_type_taxonomy):
    female_wash_item = transport.items.create({
        'body': 'Message from female in WASH category',
    })

    male_wash_item = transport.items.create({
        'body': 'Message from male in WASH category',
    })

    wash_term = TermFactory(name='WASH', taxonomy=item_type_taxonomy)
    transport.items.add_terms(
        female_wash_item['id'], wash_term.taxonomy.slug, wash_term.name)
    transport.items.add_terms(
        male_wash_item['id'], wash_term.taxonomy.slug, wash_term.name)

    tags = TaxonomyFactory(name='tags')
    female_term = TermFactory(name='female', taxonomy=tags)
    male_term = TermFactory(name='male', taxonomy=tags)
    transport.items.add_terms(
        female_wash_item['id'], female_term.taxonomy.slug, female_term.name)
    transport.items.add_terms(
        male_wash_item['id'], male_term.taxonomy.slug, male_term.name)

    page = TabbedPageFactory()
    tab_instance = TabInstanceFactory(page=page)
    request = Mock(GET={'category': 'WASH'})
    tab = ViewAndEditTableTab()
    context_data = tab.get_context_data(
        tab_instance, request, categories=[item_type_taxonomy.slug],
        filters={'terms': ['tags:female']}
    )

    table = context_data['table']

    ids = [t['id'] for t in table.data.data]

    assert ids == [female_wash_item['id']]


@pytest.mark.django_db
def test_table_items_filtered_by_date_range():
    too_old = transport.items.create({
        'body': "Too old item",
        'timestamp': '2018-10-25 23:59:59'
    })

    in_range_1 = transport.items.create({
        'body': "In range item 1",
        'timestamp': '2018-10-26 00:00:00'
    })

    in_range_2 = transport.items.create({
        'body': "In range item 1",
        'timestamp': '2018-10-27 00:00:00'
    })

    too_new = transport.items.create({
        'body': "Too new item",
        'timestamp': '2018-10-27 00:00:01'
    })

    page = TabbedPageFactory()
    tab_instance = TabInstanceFactory(page=page)
    request = Mock(GET={
        'start_time': '2018-10-26',
        'end_time': '2018-10-27',
    })
    tab = ViewAndEditTableTab()
    context_data = tab.get_context_data(
        tab_instance, request, categories=[],
        dynamic_filters=['time_range']
    )

    table = context_data['table']

    ids = [t['id'] for t in table.data.data]

    assert in_range_1['id'] in ids
    assert in_range_2['id'] in ids

    assert too_old['id'] not in ids
    assert too_new['id'] not in ids


@pytest.mark.django_db
def test_dynamic_filters_read_from_tab_instance():
    page = TabbedPageFactory(name='main')
    tab_instance = TabInstanceFactory(page=page)
    request = Mock(GET={})
    tab = ViewAndEditTableTab()

    context_data = tab.get_context_data(tab_instance,
                                        request,
                                        dynamic_filters=['category'])

    assert context_data['dynamic_filters'] == ['category']


@pytest.mark.django_db
def test_category_options_in_context_data(item_type_taxonomy):
    Term.objects.get_or_create(name='WASH', taxonomy=item_type_taxonomy)
    Term.objects.get_or_create(name='GBV', taxonomy=item_type_taxonomy)
    Term.objects.get_or_create(name='Child Protection',
                               taxonomy=item_type_taxonomy)

    page = TabbedPageFactory(name='main')
    tab_instance = TabInstanceFactory(page=page)
    request = Mock(GET={})
    tab = ViewAndEditTableTab()

    context_data = tab.get_context_data(tab_instance,
                                        request,
                                        categories=[item_type_taxonomy.slug])

    assert len(context_data['category_options']) > 0

    terms = Term.objects.filter(taxonomy=item_type_taxonomy).order_by('name')

    expected_options = [(t.name, t.name) for t in terms]

    assert context_data['category_options'] == tuple(expected_options)
