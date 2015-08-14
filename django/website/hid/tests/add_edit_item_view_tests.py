from datetime import datetime
import pytest

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.test import RequestFactory

import transport
from ..views.item import AddEditItemView

from .views_tests import (
    assert_message,
    fix_messages,
)

@pytest.fixture
def item():
    msg = {
        'body': "What is the cuse of Ebola?",
        'timestamp': "2015-02-23 00:00:00",
    }
    response = transport.items.create(msg)

    return response


@pytest.fixture
def view(item):
    view = AddEditItemView()
    view.item = item

    url = reverse('item-edit',
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


@pytest.mark.django_db
def test_item_can_be_updated(view, form):
    view.item_type = {'long_name': 'Question'}

    new_text = "What is the cause of Ebola?"
    form.cleaned_data['body'] = new_text,

    view.form_valid(form)
    item = transport.items.get(view.item['id'])

    assert item['body'] == new_text


@pytest.mark.django_db
def test_item_update_logs_message_and_redirects(view, form):
    view.item_type = {'long_name': 'Question'}

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
