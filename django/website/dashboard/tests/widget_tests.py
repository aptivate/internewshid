from mock import patch

from django.test import TestCase

from dashboard.templatetags.render_widget import render_widget
from dashboard.widget_pool import register_widget, get_widget


class TestWidget(object):
    """ A test widget with a template name and an implementation of
        of get_context_data
    """
    template_name = 'test-widget-template'

    def get_context_data(self, **kwargs):
        return {
            'is_test_widget': True,
            'value': kwargs['setting']
        }


class TestWidgetNoContextData(object):
    """ A test widget with a template name, and which does not
        implement get_context_data
    """
    template_name = 'something.html'


class TestWidgetNoTemplateName(object):
    """ A test widget without a template name, and with an
        implementation of get_context_data
    """
    def get_context_data(self, **kwargs):
        return {}


class MockWidgetInstance(object):
    """ A Mock class to represent a windget instance

    Args:
        widget_type: The widget type to associate with this
                     instance
    """
    widget_type = 'test-widget'
    settings = {
        'setting': 'carrot'
    }

    def __init__(self, widget_type):
        self.widget_type = widget_type


class WidgetPoolTestCase(TestCase):
    def setUp(self):
        # Setup the main widget and widget instance
        self.test_widget = TestWidget()
        register_widget('test-widget', self.test_widget)
        self.widget_instance = MockWidgetInstance('test-widget')
        # Setup the widget & instance without get_context_data
        # implementation
        self.test_widget_no_ctx = TestWidgetNoContextData()
        register_widget(
            'test-widget-no-ctx',
            self.test_widget_no_ctx
        )
        self.widget_instance_no_ctx = MockWidgetInstance('test-widget-no-ctx')
        # Setup the widget & instance without the template name
        self.test_widget_no_tpl = TestWidgetNoTemplateName()
        register_widget(
            'test-widget-no-tpl',
            self.test_widget_no_tpl
        )
        self.widget_instance_no_tpl = MockWidgetInstance('test-widget-no-tpl')

    def test_widget_is_registered(self):
        self.assertEqual(self.test_widget, get_widget('test-widget'))

    def test_registering_twice_overrides_existing_widget(self):
        test_widget_2 = TestWidget()
        try:
            register_widget('test-widget', test_widget_2)
            self.assertEqual(test_widget_2, get_widget('test-widget'))
        finally:
            # Clean up.
            register_widget('test-widget', self.test_widget)

    @patch('dashboard.templatetags.render_widget.render_to_string')
    def test_render_widget_loads_widget_type(self, mock_render_to_string):
        render_widget(self.widget_instance)
        self.assertTrue(
            mock_render_to_string.call_args[0][1]['is_test_widget']
        )

    @patch('dashboard.templatetags.render_widget.render_to_string')
    def test_render_widget_uses_template_name(self, mock_render_to_string):
        render_widget(self.widget_instance)
        self.assertEqual(
            mock_render_to_string.call_args[0][0],
            'test-widget-template'
        )

    @patch('dashboard.templatetags.render_widget.render_to_string')
    def test_render_widget_calls_get_context_data(self, mock_render_to_string):
        """ Test render widget calls get_context_data with the widget
            instance settings.
        """
        render_widget(self.widget_instance)
        self.assertEqual(
            mock_render_to_string.call_args[0][1]['value'],
            'carrot'
        )

    @patch('dashboard.templatetags.render_widget.render_to_string')
    def test_render_widget_without_get_ctx_data(self, mock_render_to_string):
        """ Test render widget accepts widget types that do not implement
            get_context_data.
        """
        render_widget(self.widget_instance_no_ctx)
        self.assertEqual(
            mock_render_to_string.call_args[0][1],
            {}
        )

    @patch('dashboard.templatetags.render_widget.render_to_string')
    def test_render_widget_without_template_name(self, mock_render_to_string):
        """ Test render widget uses a default template when template_name
            is missing from the widget type object
        """
        render_widget(self.widget_instance_no_tpl)
        self.assertEqual(
            mock_render_to_string.call_args[0][0],
            'dashboard/widget-missing-template.html'
        )
