import pytest

from ..tab_pool import (
    BasicHtmlTab, MissingTabError, clear_tabs, get_tab, register_tab
)


@pytest.fixture
def tab():
    return BasicHtmlTab()


def setup_function(function):
    clear_tabs()


def test_tab_is_registered(tab):
    register_tab('test-tab', tab)
    assert get_tab('test-tab') == tab


def test_exception_when_tab_not_registered(tab):
    with pytest.raises(MissingTabError) as excinfo:
        get_tab('test-tab')

    assert "Tab named 'test-tab' has not been registered" in str(excinfo.value)


def test_registering_twice_overrides_existing_tab(tab):
    register_tab('test-tab', tab)

    tab2 = BasicHtmlTab()
    register_tab('test-tab', tab2)

    assert get_tab('test-tab') == tab2
