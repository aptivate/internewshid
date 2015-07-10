import mock
import pytest

from django.contrib.messages.storage.fallback import FallbackStorage
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.test import RequestFactory

from ..views import get_deleted, process_items, get_categories, delete_items
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


def test_get_deleted_returns_empty_list_on_empty_selection():
    params = mock.MagicMock()
    params.getlist.return_value = []

    assert get_deleted(params) == []


def test_get_deleted_returns_submitted_values_as_ints():
    params = mock.MagicMock()
    params.getlist.return_value = ["201", "199", "3"]

    assert get_deleted(params) == [201, 199, 3]


def test_get_categories_returns_id_category_pairs():
    post_params = {
        'category-123': "second",
        'category-99': "third",
        'category-56': "first",
        'category-1': "second",
    }
    expected = [
        (123, "second"),
        (99, "third"),
        (56, "first"),
        (1, "second")
    ]
    assert sorted(get_categories(post_params)) == sorted(expected)  # Order is not important


def test_get_categories_filters_out_non_categories():
    post_params = {
        'category-123': "second",
        'category-99': "third",
        'notcat-1': "second",
    }
    expected = [
        (123, "second"),
        (99, "third"),
    ]
    assert sorted(get_categories(post_params)) == sorted(expected)  # Order is not important


def test_get_categories_filters_out_removed():
    post_params = {
        'category-123': "second",
        'category-99': "third",
        'category-56': "first",
        'category-1': "second",
    }
    removed = [1, 56]
    expected = [
        (123, "second"),
        (99, "third"),
    ]
    assert sorted(get_categories(post_params, removed)) == sorted(expected)  # Order is not important


@pytest.fixture
def request_item():
    '''Create item and request'''
    msg = {'body': "Message text"}
    transport.items.create(msg)

    [item] = list(transport.items.list())

    url = reverse('data-view-process')
    request = ReqFactory.post(url, {'delete': [item['id']]})
    request = fix_messages(request)

    return [request, item]


def check_item_was_deleted(request):
    assert check_message(request, u"Successfully deleted 1 item.") is True

    items = list(transport.items.list())
    assert len(list(items)) == 0


@pytest.mark.django_db
def test_delete_items_deletes_items(request_item):
    req, item = request_item
    delete_items(req, [item['id']])
    check_item_was_deleted(req)


@pytest.mark.django_db
def test_process_items_deletes_items(request_item):
    req, item = request_item
    process_items(req)
    check_item_was_deleted(req)


def test_process_items_always_redirects_to_data_view():
    url = reverse('data-view-process')
    redirect_url = reverse('data-view')

    request = ReqFactory.get(url)

    response = process_items(request)
    assert response.url == redirect_url
    assert isinstance(response, HttpResponseRedirect) is True

    request.method = 'POST'
    request = ReqFactory.post(url)
    response = process_items(request)
    assert response.url == redirect_url
    assert isinstance(response, HttpResponseRedirect) is True
