import pytest

from ..tab_pool import (
    register_tab,
    get_tab,
    clear_tabs,
    MissingTabError,
    BasicHtmlTab,
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
    with pytest.raises(MissingTabError):
        get_tab('test-tab')


def test_registering_twice_overrides_existing_tab(tab):
    register_tab('test-tab', tab)

    tab2 = BasicHtmlTab()
    register_tab('test-tab', tab2)

    assert get_tab('test-tab') == tab2
