import pytest
from mock import Mock, patch

from ..tab_pool import BasicHtmlTab, clear_tabs, register_tab
from ..templatetags.render_tab import render_tab
from .factories import TabbedPageFactory, TabInstanceFactory


class MockTabInstance(object):
    pass


render_to_string_method = 'tabbed_page.templatetags.render_tab.render_to_string'


def setup_function(function):
    clear_tabs()


@pytest.mark.django_db
@patch(render_to_string_method)
def test_uses_template_name(mock_render):
    tab = BasicHtmlTab()
    register_tab('basic-html-tab', tab)

    page = TabbedPageFactory()

    tab_instance = TabInstanceFactory(
        page=page, tab_type='basic-html-tab')

    render_tab({}, tab_instance)

    args, _ = mock_render.call_args
    assert args[0] == tab.template_name


@pytest.mark.django_db
@patch(render_to_string_method)
def test_uses_context(mock_render):
    test_context = {'is_test_tab': True}

    with patch.object(BasicHtmlTab, 'get_context_data') as mock_get_context:
        mock_get_context.return_value = test_context

        tab = BasicHtmlTab()
        register_tab('basic-html-tab', tab)

        page = TabbedPageFactory()
        tab_instance = TabInstanceFactory(page=page, tab_type='basic-html-tab')

        render_tab({}, tab_instance)

    _, kwargs = mock_render.call_args
    assert kwargs['context'] == test_context


@pytest.mark.django_db
@patch(render_to_string_method)
def test_uses_request(mock_render):
    tab = BasicHtmlTab()
    register_tab('basic-html-tab', tab)

    page = TabbedPageFactory()

    tab_instance = TabInstanceFactory(
        page=page,
        tab_type='basic-html-tab')

    request = Mock()
    context = {'request': request}
    render_tab(context, tab_instance)

    _, kwargs = mock_render.call_args
    assert kwargs['request'] == request


@pytest.mark.django_db
@patch(render_to_string_method)
def test_missing_widget_handled(mock_render):
    page = TabbedPageFactory()
    tab_instance = TabInstanceFactory(
        page=page,
        tab_type='basic-html-tab')

    context = {}
    render_tab(context, tab_instance)

    args, kwargs = mock_render.call_args
    assert args[0] == 'tabbed_page/tab-error.html'
    assert kwargs['context']['error'] == "Tab named 'basic-html-tab' has not been registered"


@pytest.mark.django_db
@patch(render_to_string_method)
def test_missing_template_handled(mock_render):
    tab = Mock()
    del tab.template_name
    register_tab('basic-html-tab', tab)

    page = TabbedPageFactory()
    tab_instance = TabInstanceFactory(
        page=page,
        tab_type='basic-html-tab')

    context = {}

    render_tab(context, tab_instance)

    args, kwargs = mock_render.call_args
    assert args[0] == 'tabbed_page/tab-error.html'
    assert kwargs['context']['error'] == "Missing template for basic-html-tab"


@pytest.mark.django_db
@patch(render_to_string_method)
def test_settings_passed_to_tab_get_context_data(render_to_string_method):
    with patch.object(BasicHtmlTab, 'get_context_data') as mock_get_context:
        tab = BasicHtmlTab()
        register_tab('basic-html-tab', tab)

        page = TabbedPageFactory()
        columns = ['body', 'timestamp', 'network_provider']
        settings = {'columns': columns}

        tab_instance = TabInstanceFactory(
            page=page,
            tab_type='basic-html-tab',
            settings=settings)

        context = {}
        render_tab(context, tab_instance)

    _, kwargs = mock_get_context.call_args
    assert kwargs['columns'] == columns


@pytest.mark.django_db
@patch(render_to_string_method)
def test_request_passed_to_tab_get_context_data(render_to_string_method):
    with patch.object(BasicHtmlTab, 'get_context_data') as mock_get_context:
        tab = BasicHtmlTab()
        register_tab('basic-html-tab', tab)

        page = TabbedPageFactory()

        tab_instance = TabInstanceFactory(
            page=page,
            tab_type='basic-html-tab')

        request = Mock()
        context = {'request': request}
        render_tab(context, tab_instance)

    args, kwargs = mock_get_context.call_args
    assert args[1] == request


@pytest.mark.django_db
@patch(render_to_string_method)
def test_tab_instance_passed_to_tab_get_context_data(render_to_string_method):
    with patch.object(BasicHtmlTab, 'get_context_data') as mock_get_context:
        tab = BasicHtmlTab()
        register_tab('basic-html-tab', tab)

        page = TabbedPageFactory()

        tab_instance = TabInstanceFactory(
            page=page,
            tab_type='basic-html-tab')

        request = Mock()
        context = {'request': request}
        render_tab(context, tab_instance)

    args, kwargs = mock_get_context.call_args
    assert args[0] == tab_instance
