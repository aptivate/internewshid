import pytest

from ..tab_pool import register_tab, get_tab


class TestTab(object):
    pass


@pytest.fixture
def tab():
    return TestTab()


@pytest.mark.django_db
def test_tab_is_registered(tab):
    register_tab('test-tab', tab)
    assert get_tab('test-tab') == tab
