from __future__ import absolute_import, unicode_literals

import pytest

from ..views import TabbedPageView
from .factories import TabbedPageFactory, TabInstanceFactory


@pytest.mark.django_db
def test_page_stored_on_view():
    page = TabbedPageFactory()
    TabbedPageFactory()

    view = TabbedPageView()
    view.kwargs = {'name': page.name}

    assert view.page == page


@pytest.mark.django_db
def test_page_defaults_to_main_when_not_set():
    page = TabbedPageFactory(name='main')
    TabbedPageFactory(name='other')

    view = TabbedPageView()
    view.kwargs = {}

    assert view.page == page


@pytest.mark.django_db
def test_name_defaults_to_main_when_empty():
    page = TabbedPageFactory(name='main')
    TabbedPageFactory(name='other')

    view = TabbedPageView()
    view.kwargs = {'name': ''}

    assert view.page == page


@pytest.mark.django_db
def test_widgets_stored_on_view_in_position_order():
    page = TabbedPageFactory()
    tab3 = TabInstanceFactory(page=page, position=3)
    tab1 = TabInstanceFactory(page=page, position=1)
    tab2 = TabInstanceFactory(page=page, position=2)

    view = TabbedPageView()
    view.kwargs = {'name': page.name}

    assert list(view.tabs) == [tab1, tab2, tab3]


@pytest.mark.django_db
def test_active_tab_is_the_default_when_none_is_specified():
    page = TabbedPageFactory()
    tabs = [
        TabInstanceFactory(page=page),
        TabInstanceFactory(page=page, default=True),
        TabInstanceFactory(page=page)
    ]

    view = TabbedPageView()
    view.kwargs = {'name': page.name, 'tab_name': None}

    assert view.active_tab == tabs[1]


@pytest.mark.django_db
def test_active_tab_is_the_specified_one():
    page = TabbedPageFactory()
    tabs = [
        TabInstanceFactory(page=page),
        TabInstanceFactory(page=page, default=True),
        TabInstanceFactory(page=page)
    ]

    view = TabbedPageView()
    view.kwargs = {'name': page.name, 'tab_name': tabs[2].name}

    assert view.active_tab == tabs[2]


@pytest.mark.django_db
def test_there_is_an_active_tab_even_without_a_default():
    page = TabbedPageFactory()
    tabs = [
        TabInstanceFactory(page=page),
        TabInstanceFactory(page=page),
        TabInstanceFactory(page=page)
    ]

    view = TabbedPageView()
    view.kwargs = {'name': page.name, 'tab_name': None}

    assert view.active_tab in tabs
