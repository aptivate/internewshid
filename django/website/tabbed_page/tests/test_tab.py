import pytest


class TestTab(object):
    def __init__(self, template_name=None, context=None):
        self.template_name = template_name

        if context is None:
            context = {}

        self.context = context

    def get_context_data(self, **kwargs):
        context = getattr(self, 'context', {})

        return context


@pytest.fixture
def tab():
    return TestTab()
