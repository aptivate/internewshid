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


@pytest.fixture
def render_to_string_method():
    return 'tabbed_page.templatetags.render_tab.render_to_string'


def get_mock_render_to_string_parameter(mock, parameter):
    """ Helper function to return arguments a mock instance
        of render_to_string has been invoked with.

        Args:
            mock: A Mock object
            parameter: either 'template_name' or 'context'
        Returns:
            The value of the given parameter for the last invocation
            of the given mock with the render_to_string signature.
        Raises:
            ValueError: If parameter is not 'template_name' or 'context'
    """
    if parameter == 'template_name':
        return mock.call_args[0][0]
    elif parameter == 'context':
        return mock.call_args[0][1]
    else:
        raise ValueError()


@pytest.mark.django_db
def test_uses_template_name(render_to_string_method):
    tab = TestTab(template_name='test-tab-template')
    register_tab('test-tab', tab)

    page = TabbedPageFactory()
    tab_instance = TabInstanceFactory(page=page, name='test-tab')

    with patch(render_to_string_method) as mock:
        render_tab(tab_instance)
        template_name = get_mock_render_to_string_parameter(
            mock, 'template_name'
        )
    assert template_name == 'test-tab-template'
