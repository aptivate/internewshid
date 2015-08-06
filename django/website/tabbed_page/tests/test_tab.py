import pytest


class TestTab(object):
    pass


@pytest.fixture
def tab():
    return TestTab()
