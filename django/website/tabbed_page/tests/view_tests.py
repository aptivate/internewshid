from __future__ import unicode_literals, absolute_import

import pytest

from django.core.urlresolvers import reverse
from django.test import RequestFactory


from django.core.urlresolvers import RegexURLResolver, NoReverseMatch

from ..views import TabbedPageView

from .factories import TabbedPageFactory


@pytest.mark.django_db
def test_name_is_name_of_page():
    page = TabbedPageFactory()

    view = TabbedPageView()
    view.kwargs = {'name': page.name}

    assert view.page_name == page.name


@pytest.mark.django_db
def test_name_defaults_to_main_when_not_set():

    view = TabbedPageView()
    view.kwargs = {}

    assert view.page_name == 'main'


@pytest.mark.django_db
def test_name_defaults_to_main_when_not_empty():

    view = TabbedPageView()
    view.kwargs = {'name': ''}

    assert view.page_name == 'main'
