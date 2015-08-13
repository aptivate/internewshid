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
    msg = {'body': "What is the cuse of Ebola?"}
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
def form(view):
    form = view.form_class('question')

    return form


@pytest.mark.django_db
def test_item_update_logs_message_and_redirects(view, form):
    view.item_type = {'long_name': 'Question'}

    form.cleaned_data = {
        'next': '/',
        'id': view.item['id'],
    }

    response = view.form_valid(form)
    assert response.url == '/'

    assert_message(view.request,
                   messages.SUCCESS,
                   "Question %s successfully updated." % view.item['id'])


@pytest.mark.django_db
def test_item_update_without_type_logs_message(view, form):
    view.item_type = None

    form.cleaned_data = {
        'next': '/',
        'id': view.item['id'],
    }

    view.form_valid(form)

    assert_message(view.request,
                   messages.SUCCESS,
                   "Item %s successfully updated." % view.item['id'])


@pytest.mark.django_db
def test_no_category_when_item_type_not_set(view):
    view.item_type = None
    initial = view.get_initial()

    assert 'category' not in initial
