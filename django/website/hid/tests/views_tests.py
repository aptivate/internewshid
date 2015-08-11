from mock import Mock
import pytest

from django.contrib.messages.storage.fallback import FallbackStorage
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, QueryDict
from django.test import RequestFactory

from hid.tabs.view_and_edit_table import (
    ViewAndEditTableTab,
    view_and_edit_table_form_process_items,
    _delete_items,
    _get_view_and_edit_form_request_parameters,
    DELETE_COMMAND,
    QUESTION_TYPE_TAXONOMY,
    REMOVE_QTYPE_COMMAND
)

from tabbed_page.tests.factories import (
    TabbedPageFactory,
    TabInstanceFactory
)

from taxonomies.tests.factories import (
    TaxonomyFactory,
    TermFactory,
)

import transport


ReqFactory = RequestFactory()


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
def test_process_items_removes_question_type():
    msg = {'body': "Message text"}
    transport.items.create(msg)

    [item] = list(transport.items.list())

    taxonomy = TaxonomyFactory(name="Ebola Questions")
    term_to_delete = TermFactory(name='term to be deleted',
                                 taxonomy=taxonomy)
    transport.items.add_term(
        item['id'], term_to_delete.taxonomy.slug, term_to_delete.name)

    term_to_keep = TermFactory(name='term not to be deleted')
    transport.items.add_term(
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
def test_upload_form_source_read_from_settings():
    page = TabbedPageFactory()
    tab_instance = TabInstanceFactory(page=page)
    request = Mock(GET={})
    tab = ViewAndEditTableTab()

    context_data = tab.get_context_data(tab_instance,
                                        request,
                                        source='rapidpro')

    form = context_data['upload_form']
    assert form.initial.get('source') == 'rapidpro'


@pytest.mark.django_db
def test_upload_form_next_url_read_from_tab_instance():
    page = TabbedPageFactory(name='main')
    tab_instance = TabInstanceFactory(page=page, name='rumors')
    request = Mock(GET={})
    tab = ViewAndEditTableTab()

    context_data = tab.get_context_data(tab_instance,
                                        request,
                                        source='rapidpro')

    form = context_data['upload_form']

    expected_url = reverse('tabbed-page',
                           kwargs={'name': 'main', 'tab_name': 'rumors'})

    assert form.initial.get('next') == expected_url


@pytest.mark.django_db
def test_no_upload_form_when_source_not_set():
    page = TabbedPageFactory(name='main')
    tab_instance = TabInstanceFactory(page=page, name='all')
    request = Mock(GET={})
    tab = ViewAndEditTableTab()

    context_data = tab.get_context_data(tab_instance,
                                        request)

    form = context_data['upload_form']

    assert form is None


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
