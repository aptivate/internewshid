from datetime import datetime
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.test import RequestFactory
from mock import patch
import pytest

from transport.exceptions import TransportException

from .views_tests import fix_messages
from ..views.item import AddEditItemView


ReqFactory = RequestFactory()


def get_view_for_request(view_class, url_name, args=None, kwargs=None,
                         request_type='get', post=None, get=None):
    """ Instanciate a class based view for the given request, and
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
            (view, response) tupple
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

    assert get_item.called
    assert get_item.call_args[0][0] == 103


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
