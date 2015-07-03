import mock
import pytest

from django.contrib.messages.storage.fallback import FallbackStorage
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.test import RequestFactory

from ..views import get_deleted, process_items
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


@pytest.mark.xfail  # Pending reimplementation of Delete via API
@pytest.mark.django_db
def test_process_items_deletes_items():
    msg = {'body': "Message text"}
    transport.create_item(msg)

    [item] = list(transport.get_items())

    url = reverse('data-view-process')
    request = ReqFactory.post(url, {'delete': [item['id']]})
    request = fix_messages(request)

    process_items(request)
    assert check_message(request, u"Successfully deleted 1 item.") is True

    items = list(transport.get_items())
    assert len(list(items)) == 0
