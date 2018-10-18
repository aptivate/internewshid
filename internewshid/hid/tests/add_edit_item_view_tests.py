from datetime import datetime

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.test import RequestFactory
from django.urls import reverse
from django.utils import timezone

import pytest
from mock import patch

from hid.constants import ITEM_TYPE_CATEGORY
from taxonomies.tests.factories import TaxonomyFactory, TermFactory
import transport
from transport.exceptions import TransportException

from ..views.item import DEFAULT_ITEM_TYPE, AddEditItemView
from .views_tests import assert_message, assert_no_messages, fix_messages


@pytest.fixture
def item():
    msg = {
        'body': "What is the cuse of Ebola?",
        'timestamp': "2015-02-23 00:00:00",
    }
    response = transport.items.create(msg)

    return response


@pytest.fixture
def item_type():
    return {'name': 'question', 'long_name': 'Question'}


@pytest.fixture
def add_view(item_type):
    view = AddEditItemView()
    view.item_type = item_type

    url = reverse('add-item', kwargs={'item_type': item_type['name']})

    factory = RequestFactory()
    view.request = factory.post(url)
    view.request = fix_messages(view.request)

    return view


@pytest.fixture
def view(item, item_type):
    view = AddEditItemView()
    view.item = item
    view.item_type = item_type

    url = reverse('edit-item',
                  kwargs={'item_id': item['id']})

    factory = RequestFactory()
    view.request = factory.post(url)
    view.request = fix_messages(view.request)

    return view


@pytest.fixture
def form(view, item):
    form = view.form_class('question')
    form.cleaned_data = item
    form.cleaned_data['next'] = '/'

    return form


ReqFactory = RequestFactory()


def get_view_for_request(view_class, url_name, args=None, kwargs=None,
                         request_type='get', post=None, get=None):
    """ Instantiate a class based view for the given request, and
        return the view object

        Args:
            view_class (Class): Class of the view
            url_name (str): Name of the url to request
            args (list): Arguments passed to reverse
            kwargs (dict): Arguments passed to reverse
            request_type (str): Type of query. Either 'get' or 'post'
            post (dict): Arguments passed to post requests
            get (dict): Arguemnts passed to get requests
        Returns:
            object: The instanced view object
    """
    if args is None:
        args = []
    if kwargs is None:
        kwargs = {}
    if post is None:
        post = {}
    if get is None:
        get = {}

    url = reverse(url_name, args=args, kwargs=kwargs)
    if request_type == 'get':
        request = ReqFactory.get(url, get)
    else:
        request = ReqFactory.post(url, post)
    request = fix_messages(request)
    view = view_class()
    view.request = request
    view.args = args
    view.kwargs = kwargs
    return view


def make_request(view_class, url_name, args=None, kwargs=None,
                 request_type='get', post=None, get=None):
    """ Perform the given request, and return the view and the response.

        Args:
            See get_view_for_request
        Returns:
            (view, response) tuple
    """
    view = get_view_for_request(view_class, url_name, args, kwargs,
                                request_type, post, get)
    if request_type == 'get':
        response = view.get(view.request, *view.args, **view.kwargs)
    else:
        response = view.post(view.request, *view.args, **view.kwargs)

    return (view, response)


@pytest.fixture
def generic_item():
    return {
        'id': 1001,
        'body': 'hello',
        'created': datetime(2015, 5, 5),
        'timestamp': datetime(2016, 6, 6),
        'last_updated': datetime(2017, 7, 7),
        'terms': [
            {
                'taxonomy': 'item-types',
                'name': 'generic',
                'long_name': 'Generic'
            },
            {
                'taxonomy': 'a-taxonomy',
                'name': 'a-term',
                'long_name': 'A Term'
            }
        ]
    }


@pytest.fixture
def item_without_item_type():
    return {
        'id': 1001,
        'body': 'hello',
        'created': datetime(2015, 5, 5),
        'timestamp': datetime(2016, 6, 6),
        'last_updated': datetime(2017, 7, 7),
        'terms': []
    }


@pytest.fixture
def an_item_type():
    return {
        'taxonomy': 'item-types',
        'name': 'an-item-type',
        'long_name': 'An Item Type'
    }


def test_the_item_is_added_to_the_view_on_get_requests(generic_item):
    with patch('hid.views.item.transport.items.get') as get_item:
        get_item.return_value = generic_item
        (view, response) = make_request(
            AddEditItemView,
            'edit-item',
            kwargs={'item_id': 103}
        )

    assert view.item == generic_item


def test_the_item_type_is_added_to_the_view_on_get_requests(generic_item):
    with patch('hid.views.item.transport.items.get') as get_item:
        get_item.return_value = generic_item
        (view, response) = make_request(
            AddEditItemView,
            'edit-item',
            kwargs={'item_id': 103}
        )

    assert view.item_type['name'] == 'generic'


def test_there_is_a_default_item_type_on_get_requests(item_without_item_type):
    default_item_type = {
        'name': 'a-default-type',
        'long_name': 'A Default Type',
        'taxonomy': 'item-types'
    }

    with patch.dict(DEFAULT_ITEM_TYPE, default_item_type):
        with patch('hid.views.item.transport.items.get') as get_item:
            get_item.return_value = item_without_item_type
            (view, response) = make_request(
                AddEditItemView,
                'edit-item',
                kwargs={'item_id': 103}
            )

        assert view.item_type == default_item_type


def test_the_item_terms_are_added_to_the_view_on_get_requests(generic_item):
    with patch('hid.views.item.transport.items.get') as get_item:
        get_item.return_value = generic_item
        (view, response) = make_request(
            AddEditItemView,
            'edit-item',
            kwargs={'item_id': 103}
        )

    assert view.item_terms == {
        'item-types': [{
            'taxonomy': 'item-types',
            'name': 'generic',
            'long_name': 'Generic'
        }],
        'a-taxonomy': [{
            'taxonomy': 'a-taxonomy',
            'name': 'a-term',
            'long_name': 'A Term'
        }]
    }


def test_the_item_is_added_to_the_view_on_post_requests(generic_item):
    with patch('hid.views.item.transport.items.get') as get_item:
        get_item.return_value = generic_item
        (view, response) = make_request(
            AddEditItemView,
            'edit-item',
            kwargs={'item_id': 103},
            request_type='post',
            post={
                'action': 'cancel',
                'next': ''
            }
        )

    assert view.item == generic_item


def test_the_item_type_is_added_to_the_view_on_post_requests(generic_item):
    with patch('hid.views.item.transport.items.get') as get_item:
        get_item.return_value = generic_item
        (view, response) = make_request(
            AddEditItemView,
            'edit-item',
            kwargs={'item_id': 103},
            request_type='post',
            post={
                'action': 'cancel',
                'next': ''
            }
        )

    assert view.item_type['name'] == 'generic'


def test_there_is_a_default_item_type_on_post_requests(item_without_item_type):
    default_item_type = {
        'name': 'a-default-type',
        'long_name': 'A Default Type',
        'taxonomy': 'item-types'
    }

    with patch.dict(DEFAULT_ITEM_TYPE, default_item_type):
        with patch('hid.views.item.transport.items.get') as get_item:
            get_item.return_value = item_without_item_type
            (view, response) = make_request(
                AddEditItemView,
                'edit-item',
                kwargs={'item_id': 103},
                request_type='post',
                post={
                    'action': 'cancel',
                    'next': ''
                }
            )

        assert view.item_type == default_item_type


def test_the_item_terms_are_added_to_the_view_on_post_requests(generic_item):
    with patch('hid.views.item.transport.items.get') as get_item:
        get_item.return_value = generic_item
        (view, response) = make_request(
            AddEditItemView,
            'edit-item',
            kwargs={'item_id': 103},
            request_type='post',
            post={
                'action': 'cancel',
                'next': ''
            }
        )

    assert view.item_terms == {
        'item-types': [{
            'taxonomy': 'item-types',
            'name': 'generic',
            'long_name': 'Generic'
        }],
        'a-taxonomy': [{
            'taxonomy': 'a-taxonomy',
            'name': 'a-term',
            'long_name': 'A Term'
        }]
    }


def test_form_initial_values_set_that_of_item(generic_item):
    with patch('hid.views.item.transport.items.get') as get_item:
        get_item.return_value = generic_item
        (view, response) = make_request(
            AddEditItemView,
            'edit-item',
            kwargs={'item_id': 103}
        )

    initial = view.get_initial()
    assert initial['id'] == 1001
    assert initial['body'] == 'hello'
    assert initial['timestamp'] == datetime(2016, 6, 6)


def test_form_next_url_is_next_query_parameter(generic_item):
    with patch('hid.views.item.transport.items.get') as get_item:
        get_item.return_value = generic_item
        (view, response) = make_request(
            AddEditItemView,
            'edit-item',
            kwargs={'item_id': 103},
            get={'next': 'http://example.com'}
        )

    initial = view.get_initial()
    assert initial['next'] == 'http://example.com'


def test_form_next_url_is_referer_if_no_next_query_parameter(generic_item):
    with patch('hid.views.item.transport.items.get') as get_item:
        get_item.return_value = generic_item
        (view, response) = make_request(
            AddEditItemView,
            'edit-item',
            kwargs={'item_id': 103}
        )

    view.request.META['HTTP_REFERER'] = '/view-edit/main/rumors'

    initial = view.get_initial()
    assert initial['next'] == '/view-edit/main/rumors'


def test_form_next_url_is_dashboard_if_nothing_else_set(generic_item):
    with patch('hid.views.item.transport.items.get') as get_item:
        get_item.return_value = generic_item
        (view, response) = make_request(
            AddEditItemView,
            'edit-item',
            kwargs={'item_id': 103}
        )

    initial = view.get_initial()
    assert initial['next'] == reverse('dashboard')


def test_context_data_includes_the_item(generic_item):
    with patch('hid.views.item.transport.items.get') as get_item:
        get_item.return_value = generic_item
        (view, response) = make_request(
            AddEditItemView,
            'edit-item',
            kwargs={'item_id': 103},
        )

    assert 'item' in response.context_data
    assert response.context_data['item']['id'] == 1001


def test_context_data_includes_item_type_label(generic_item):
    with patch('hid.views.item.transport.items.get') as get_item:
        get_item.return_value = generic_item
        (view, response) = make_request(
            AddEditItemView,
            'edit-item',
            kwargs={'item_id': 103},
        )

    assert 'item_type_label' in response.context_data
    assert response.context_data['item_type_label'] == 'Generic'


def test_correct_item_is_fetched_during_request(generic_item):
    with patch('hid.views.item.transport.items.get') as get_item:
        get_item.return_value = generic_item
        make_request(
            AddEditItemView,
            'edit-item',
            kwargs={'item_id': 103},
        )

    (args, _) = get_item.call_args
    assert get_item.called
    assert args[0] == 103


def test_displaying_existing_item_returns_template_response(generic_item):
    with patch('hid.views.item.transport.items.get') as get_item:
        get_item.return_value = generic_item
        (view, response) = make_request(
            AddEditItemView,
            'edit-item',
            kwargs={'item_id': 103},
        )

    assert type(response) is TemplateResponse


def test_displaying_unknown_item_returns_redirect_response(generic_item):
    with patch('hid.views.item.transport.items.get') as get_item:
        get_item.side_effect = TransportException()
        get_item.return_value = generic_item
        (view, response) = make_request(
            AddEditItemView,
            'edit-item',
            kwargs={'item_id': 103},
        )

    assert type(response) is HttpResponseRedirect


def test_add_new_item_get_request_populates_item_type(an_item_type):
    with patch('hid.views.item.transport.terms.list') as list_term:
        list_term.return_value = [an_item_type]
        (view, response) = make_request(
            AddEditItemView,
            'add-item',
            kwargs={'item_type': 'an-item-type'},
        )

    assert view.item_type == an_item_type


def test_add_new_item_post_request_populates_item_type(an_item_type):
    with patch('hid.views.item.transport.terms.list') as list_term:
        list_term.return_value = [an_item_type]
        (view, response) = make_request(
            AddEditItemView,
            'add-item',
            kwargs={'item_type': 'an-item-type'},
            request_type='post',
            post={
                'action': 'save',
                'next': ''
            }
        )

    assert view.item_type == an_item_type


def test_add_new_item_returns_template_response(an_item_type):
    with patch('hid.views.item.transport.terms.list') as list_term:
        list_term.return_value = [an_item_type]
        (view, response) = make_request(
            AddEditItemView,
            'add-item',
            kwargs={'item_type': 'an-item-type'},
        )

    assert type(response) is TemplateResponse


def test_add_new_item_with_unknown_item_type_redirects():
    with patch('hid.views.item.transport.terms.list') as list_term:
        list_term.return_value = []
        (view, response) = make_request(
            AddEditItemView,
            'add-item',
            kwargs={'item_type': 'an-item-type'},
        )

    assert type(response) is HttpResponseRedirect


@pytest.mark.django_db
def test_submitting_form_with_id_equal_0_creates_an_item(item_type):
    body = 'Hello, here is a new item'
    the_time = datetime(2015, 06, 27, 0, 0)
    (view, response) = make_request(
        AddEditItemView,
        'add-item',
        kwargs={'item_type': item_type['name']},
        request_type='post',
        post={
            'action': 'save',
            'timestamp': the_time,
            'next': '/',
            'id': 0,
            'body': body
        }
    )

    assert view.item['id'] > 0
    item = transport.items.get(view.item['id'])
    assert item is not None


@pytest.mark.django_db
def test_submitting_form_creates_an_item_with_correct_fields(item_type):
    body = 'Hello, here is a new item'
    the_time = datetime(2015, 06, 27, 0, 0)
    (view, response) = make_request(
        AddEditItemView,
        'add-item',
        kwargs={'item_type': item_type['name']},
        request_type='post',
        post={
            'action': 'save',
            'timestamp': the_time,
            'next': '/',
            'id': 0,
            'body': body
        }
    )

    assert view.item['id'] > 0
    item = transport.items.get(view.item['id'])
    assert item['body'] == body
    assert timezone.make_naive(item['timestamp']) == the_time


@pytest.mark.django_db
def test_submitting_form_creates_an_item_with_a_category(item_type):
    taxonomy = TaxonomyFactory(name=ITEM_TYPE_CATEGORY['question'])
    TermFactory(taxonomy=taxonomy, name='Ebola updates',
                long_name='What are the current updates on Ebola.')

    body = 'Hello, here is a new item'
    (view, response) = make_request(
        AddEditItemView,
        'add-item',
        kwargs={'item_type': item_type['name']},
        request_type='post',
        post={
            'action': 'save',
            'timestamp': datetime.now(),
            'next': '/',
            'id': 0,
            'category': 'Ebola updates',
            'body': body
        }
    )

    assert view.item['id'] > 0
    item = transport.items.get(view.item['id'])
    expected_term = {
        'taxonomy': taxonomy.name,
        'name': 'Ebola updates',
        'long_name': 'What are the current updates on Ebola.'
    }

    assert expected_term in item['terms']


@pytest.mark.django_db
def test_item_can_be_updated(view, form):
    new_text = "What is the cause of Ebola?"
    form.cleaned_data['body'] = new_text,

    view.form_valid(form)
    item = transport.items.get(view.item['id'])

    assert item['body'] == new_text


@pytest.mark.django_db
def test_item_category_can_be_updated(view, form):
    taxonomy = TaxonomyFactory(name=ITEM_TYPE_CATEGORY['question'])
    TermFactory(taxonomy=taxonomy, name='Ebola updates')

    form.cleaned_data['category'] = 'Ebola updates',

    view.form_valid(form)
    item = transport.items.get(view.item['id'])

    terms = {t['taxonomy']: t['name'] for t in item['terms']}

    assert terms[taxonomy.name] == 'Ebola updates'


@pytest.mark.django_db
def test_item_category_can_be_unset(view, form):
    taxonomy = TaxonomyFactory(name=ITEM_TYPE_CATEGORY['question'])
    TermFactory(taxonomy=taxonomy, name='Ebola origins')

    transport.items.add_terms(view.item['id'], taxonomy.name,
                              'Ebola origins')

    form.cleaned_data['category'] = ''

    view.form_valid(form)
    item = transport.items.get(view.item['id'])

    terms = {t['taxonomy']: t['name'] for t in item['terms']}

    assert taxonomy.name not in terms


@pytest.mark.django_db
def test_item_category_not_required(view, form):
    taxonomy = TaxonomyFactory(name=ITEM_TYPE_CATEGORY['question'])
    TermFactory(taxonomy=taxonomy, name='Ebola origins')

    form.cleaned_data['category'] = ''

    view.form_valid(form)
    item = transport.items.get(view.item['id'])

    terms = {t['taxonomy']: t['name'] for t in item['terms']}

    assert taxonomy.name not in terms


@pytest.mark.django_db
def test_item_update_logs_message_and_redirects(view, form):
    taxonomy = TaxonomyFactory(name=ITEM_TYPE_CATEGORY['question'])
    TermFactory(taxonomy=taxonomy, name='Ebola origins')

    view.item_type['long_name'] = 'Question'

    response = view.form_valid(form)
    assert response.url == form.cleaned_data['next']

    assert_message(view.request,
                   messages.SUCCESS,
                   "Question %s successfully updated." % view.item['id'])


@pytest.mark.django_db
def test_item_update_transport_exception_logs_message(view, form):
    # This could happen if someone else deletes the item when the
    # form is open
    transport.items.delete(view.item['id'])

    view.form_valid(form)

    assert_message(view.request,
                   messages.ERROR,
                   "Not found.")


@pytest.mark.django_db
def test_item_term_update_transport_exception_logs_message(view, form):
    taxonomy = TaxonomyFactory(name=ITEM_TYPE_CATEGORY['question'])

    # This shouldn't be possible from the form but we may get other
    # TransportException errors
    form.cleaned_data['category'] = "A category that doesn't exist"
    view.form_valid(form)

    assert_message(view.request,
                   messages.ERROR,
                   "Term matching query does not exist.")


@pytest.mark.django_db
def test_item_term_delete_transport_exception_logs_message(view, form):
    taxonomy = TaxonomyFactory(name=ITEM_TYPE_CATEGORY['question'])

    # This shouldn't be possible from the form but we may get other
    # TransportException errors
    form.cleaned_data['category'] = ''

    # Not sure if this is good practice
    ITEM_TYPE_CATEGORY['question'] = 'unknown-slug'

    view.form_valid(form)

    ITEM_TYPE_CATEGORY['question'] = 'ebola-questions'

    assert_message(view.request,
                   messages.ERROR,
                   "Taxonomy with slug 'unknown-slug' does not exist.")


@pytest.mark.django_db
def test_item_can_be_deleted(view, form):
    view._delete_item()

    assert_message(view.request,
                   messages.SUCCESS,
                   "Question %s successfully deleted." % view.item['id'])

    with pytest.raises(TransportException) as excinfo:
        transport.items.get(view.item['id'])

    assert excinfo.value.message['status_code'] == 404


@pytest.mark.django_db
def test_free_tags_created_on_item_update(view, form):
    # Deliberate spaces to be stripped
    form.cleaned_data['tags'] = 'Monrovia , Important ,age 35-40'

    view.form_valid(form)
    assert_no_messages(view.request, messages.ERROR)

    item = transport.items.get(view.item['id'])

    terms = [t['name'] for t in item['terms']]
    assert 'Monrovia' in terms
    assert 'Important' in terms
    assert 'age 35-40' in terms

    taxonomies = [t['taxonomy'] for t in item['terms']]
    assert 'tags' in taxonomies


@pytest.mark.django_db
def test_existing_tag_deleted_on_item_update(view, form):
    transport.items.add_terms(view.item['id'], 'tags', ['age 35-40'])

    form.cleaned_data['tags'] = 'Monrovia'

    view.form_valid(form)
    assert_no_messages(view.request, messages.ERROR)

    item = transport.items.get(view.item['id'])

    terms = [t['name'] for t in item['terms']]
    assert 'Monrovia' in terms
    assert 'age 35-40' not in terms


@pytest.mark.django_db
def test_free_tags_created_for_new_item(add_view, form):
    form.cleaned_data['tags'] = 'Monrovia,Important,age 35-40'
    form.cleaned_data['id'] = 0

    add_view.form_valid(form)
    assert_no_messages(add_view.request, messages.ERROR)

    item = transport.items.get(add_view.item['id'])

    terms = [t['name'] for t in item['terms']]
    assert 'Monrovia' in terms
    assert 'Important' in terms
    assert 'age 35-40' in terms

    taxonomies = [t['taxonomy'] for t in item['terms']]
    assert 'tags' in taxonomies


@pytest.mark.django_db
def test_data_origin_created_for_new_item(add_view, form):
    form.cleaned_data['id'] = 0

    add_view.form_valid(form)
    assert_no_messages(add_view.request, messages.ERROR)

    item = transport.items.get(add_view.item['id'])

    terms = [t['name'] for t in item['terms']]
    assert 'Form Entry' in terms

    taxonomies = [t['taxonomy'] for t in item['terms']]
    assert 'data-origins' in taxonomies


@pytest.mark.django_db
def test_form_initial_values_include_tags(generic_item):
    with patch('hid.views.item.transport.items.get') as get_item:
        generic_item['terms'] = [
            {
                'taxonomy': 'tags',
                'name': 'Monrovia',
                'long_name': 'Monrovia',
            },
            {
                'taxonomy': 'tags',
                'name': 'age 35-40',
                'long_name': 'Age 35-40',
            },
            {
                'taxonomy': 'tags',
                'name': 'interesting',
                'long_name': 'Interesting',
            },
        ]

        get_item.return_value = generic_item

        (view, response) = make_request(
            AddEditItemView,
            'edit-item',
            kwargs={'item_id': 103}
        )

    initial = view.get_initial()
    assert initial['tags'] == 'Monrovia,age 35-40,interesting'
