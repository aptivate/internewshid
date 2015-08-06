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

    render_tab(None, tab_instance)

    args, _ = mock_render.call_args
    assert args[0] == 'test-tab-template'


@pytest.mark.django_db
@patch(render_to_string_method)
def test_uses_context(mock_render):
    test_context = {'is_test_tab': True}

    tab = TestTab(context=test_context)
    register_tab('test-tab', tab)

    page = TabbedPageFactory()

    tab_instance = TabInstanceFactory(page=page, name='test-tab')

    render_tab(None, tab_instance)

    _, kwargs = mock_render.call_args
    assert kwargs['context'] == test_context


@pytest.mark.django_db
@patch(render_to_string_method)
def test_uses_request(mock_render):
    tab = TestTab()
    register_tab('test-tab', tab)

    page = TabbedPageFactory()
    tab_instance = TabInstanceFactory(page=page, name='test-tab')

    request = 'a request'
    context = {'request': request}
    render_tab(context, tab_instance)

    _, kwargs = mock_render.call_args
    assert kwargs['request'] == request


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
        render_tab(None, tab_instance)

    _, kwargs = mock_get_context.call_args
    assert kwargs['columns'] == columns
