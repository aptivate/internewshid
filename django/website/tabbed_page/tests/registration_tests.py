import pytest

from ..tab_pool import (
    register_tab,
    get_tab,
    clear_tabs,
    MissingTabError,
)


def setup_function(function):
    clear_tabs()


class TestTab(object):
    pass


@pytest.fixture
def tab():
    return TestTab()


def test_tab_is_registered(tab):
    register_tab('test-tab', tab)
    assert get_tab('test-tab') == tab


def test_exception_when_tab_not_registered(tab):
    with pytest.raises(MissingTabError):
        get_tab('test-tab')
