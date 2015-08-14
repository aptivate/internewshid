from datetime import datetime
from mock import patch
import pytest

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.test import RequestFactory

import transport
from ..views.item import AddEditItemView

from .views_tests import (
    assert_message,
    fix_messages,
)

from transport.exceptions import TransportException


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


def test_form_next_url_value_set_to_current_url_by_default(generic_item):
    with patch('hid.views.item.transport.items.get') as get_item:
        get_item.return_value = generic_item
        (view, response) = make_request(
            AddEditItemView,
            'edit-item',
            kwargs={'item_id': 103}
        )

    initial = view.get_initial()
    assert initial['next'] == reverse('edit-item', kwargs={'item_id': 103})


def test_form_next_url_value_set_to_provided_url(generic_item):
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


@pytest.mark.django_db
def test_item_can_be_updated(view, form):
    new_text = "What is the cause of Ebola?"
    form.cleaned_data['body'] = new_text,

    view.form_valid(form)
    item = transport.items.get(view.item['id'])

    assert item['body'] == new_text


@pytest.mark.django_db
def test_item_category_can_be_updated(view, form):
    form.cleaned_data['category'] = 'Ebola updates',

    view.form_valid(form)
    item = transport.items.get(view.item['id'])

    terms = {t['taxonomy']: t['name'] for t in item['terms']}

    assert terms['ebola-questions'] == 'Ebola updates'


@pytest.mark.django_db
def test_item_category_can_be_unset(view, form):
    transport.items.add_term(view.item['id'], 'ebola-questions',
                             'Ebola origins')

    form.cleaned_data['category'] = ''

    view.form_valid(form)
    item = transport.items.get(view.item['id'])

    terms = {t['taxonomy']: t['name'] for t in item['terms']}

    assert 'ebola-questions' not in terms


@pytest.mark.django_db
def test_item_category_not_required(view, form):
    form.cleaned_data['category'] = ''

    view.form_valid(form)
    item = transport.items.get(view.item['id'])

    terms = {t['taxonomy']: t['name'] for t in item['terms']}

    assert 'ebola-questions' not in terms


@pytest.mark.django_db
def test_item_update_logs_message_and_redirects(view, form):
    view.item_type['long_name'] = 'Question'

    response = view.form_valid(form)
    assert response.url == form.cleaned_data['next']

    assert_message(view.request,
                   messages.SUCCESS,
                   "Question %s successfully updated." % view.item['id'])


@pytest.mark.django_db
def test_item_update_without_type_logs_message(view, form):
    view.item_type = None

    view.form_valid(form)

    assert_message(view.request,
                   messages.SUCCESS,
                   "Item %s successfully updated." % view.item['id'])


@pytest.mark.django_db
def test_no_category_when_item_type_not_set(view):
    view.item_type = None
    initial = view.get_initial()

    assert 'category' not in initial


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
    # This shouldn't be possible from the form but we may get other
    # TransportException errors
    form.cleaned_data['category'] = "A category that doesn't exist"
    view.form_valid(form)

    assert_message(view.request,
                   messages.ERROR,
                   "Term matching query does not exist.")


@pytest.mark.django_db
def test_item_term_delete_transport_exception_logs_message(view, form):
    # This shouldn't be possible from the form but we may get other
    # TransportException errors
    form.cleaned_data['category'] = ''

    # Not sure if this is good practice
    from ..constants import ITEM_TYPE_CATEGORY
    ITEM_TYPE_CATEGORY['question'] = 'unknown-slug'

    view.form_valid(form)

    ITEM_TYPE_CATEGORY['question'] = 'ebola-questions'

    assert_message(view.request,
                   messages.ERROR,
                   "Taxonomy with slug 'unknown-slug' does not exist.")
