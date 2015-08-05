from mock import patch
import pytest

from .factories import (
    TabbedPageFactory,
    TabInstanceFactory,
)
from ..tab_pool import register_tab
from ..templatetags.render_tab import render_tab

from .test_tab import TestTab


class MockTabInstance(object):
    pass


render_to_string_method = 'tabbed_page.templatetags.render_tab.render_to_string'


@pytest.mark.django_db
@patch(render_to_string_method)
def test_uses_template_name(mock_render):
    tab = TestTab(template_name='test-tab-template')
    register_tab('test-tab', tab)

    page = TabbedPageFactory()
    tab_instance = TabInstanceFactory(page=page, name='test-tab')

    render_tab(tab_instance)

    mock_render.assert_called_once_with('test-tab-template', {})


@pytest.mark.django_db
@patch(render_to_string_method)
def test_uses_context(mock_render):
    test_context = {'is_test_tab': True}

    tab = TestTab(context=test_context)
    register_tab('test-tab', tab)

    page = TabbedPageFactory()

    tab_instance = TabInstanceFactory(page=page, name='test-tab')

    render_tab(tab_instance)

    mock_render.assert_called_once_with(None, test_context)


@pytest.mark.django_db
@patch(render_to_string_method)
def test_settings_passed_to_widget_get_context_data(render_to_string_method):
    with patch.object(TestTab, 'get_context_data') as mock_get_context:
        tab = TestTab()
        register_tab('test-tab', tab)

        page = TabbedPageFactory()
        columns = ['body', 'timestamp', 'network_provider']
        settings = {'columns': columns}
        tab_instance = TabInstanceFactory(page=page,
                                          name='test-tab',
                                          settings=settings)
        render_tab(tab_instance)

    mock_get_context.assert_called_once_with(columns=columns)
