from __future__ import unicode_literals, absolute_import
import pytest

from ..views import TabbedPageView

from .factories import TabbedPageFactory, TabFactory


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
    tab3 = TabFactory(page=page, position=3)
    tab1 = TabFactory(page=page, position=1)
    tab2 = TabFactory(page=page, position=2)

    view = TabbedPageView()
    view.kwargs = {'name': page.name}

    assert list(view.tabs) == [tab1, tab2, tab3]
