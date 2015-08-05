import pytest


class TestTab(object):
    def __init__(self, template_name=None):
        self.template_name = template_name


@pytest.fixture
def tab():
    return TestTab()
