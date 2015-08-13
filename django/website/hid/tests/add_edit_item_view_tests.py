import pytest

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.test import RequestFactory

from ..views.item import AddEditItemView
from .views_tests import (
    assert_message,
    fix_messages,
)

@pytest.fixture
def item():
    return {'id': "1234"}


@pytest.fixture
def view(item):
    view = AddEditItemView()

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
def test_item_update_logs_message_and_redirects(view, form, item):
    view.item_type = {'long_name': 'Question'}

    form.cleaned_data = {
        'next': '/',
        'id': item['id'],
    }

    response = view.form_valid(form)
    assert response.url == '/'

    assert_message(view.request,
                   messages.SUCCESS,
                   "Question 1234 successfully updated.")


@pytest.mark.django_db
def test_item_update_without_type_logs_message(view, form, item):
    view.item_type = None

    form.cleaned_data = {
        'next': '/',
        'id': item['id'],
    }

    view.form_valid(form)

    assert_message(view.request,
                   messages.SUCCESS,
                   "Item %s successfully updated." % item['id'])
