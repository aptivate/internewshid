from django.test import TestCase

from mock import patch

from dashboard.templatetags.render_widget import render_widget
from dashboard.widget_pool import WidgetError, get_widget, register_widget


class CustomTestWidget(object):
    """ A test widget with a template name and an implementation of
        of get_context_data
    """
    def __init__(self, template_name=None, context=None):
        self.template_name = template_name
        self.context = context

    def get_context_data(self, **kwargs):
        if self.context:
            ret = dict(self.context)
        else:
            ret = {}
        ret['kwargs'] = kwargs
        return ret


class CustomTestWidgetNoContextData(object):
    """ A test widget with a template name, and which does not
        implement get_context_data
    """
    template_name = 'something.html'


class CustomTestWidgetNoTemplateName(object):
    """ A test widget without a template name, and with an
        implementation of get_context_data
    """
    def get_context_data(self, **kwargs):
        return {}


class CustomTestWidgetRaisesException(object):
    """ A test widget which raises a generic exception in
        get_context_data
    """
    template_name = 'something.html'

    def get_context_data(self, **kwargs):
        raise Exception('message raised from get_context_data')


class CustomTestWidgetRaisesWidgetError(object):
    """ A test widget which raises a WidgetError in
        get_context_data
    """
    template_name = 'something.html'

    def get_context_data(self, **kwargs):
        raise WidgetError('message raised from get_context_data')


class MockWidgetInstance(object):
    """ A Mock class to represent a widget instance

    Args:
        widget_type: The widget type to associate with this
                     instance
    """
    def __init__(self, widget_type, settings=None):
        self.widget_type = widget_type
        if settings is not None:
            self.settings = settings
        else:
            self.settings = {}


class WidgetPoolTestCase(TestCase):
    def setUp(self):
        # Path to the render_to_string method we want to patch for some of
        # the tests.
        self.render_to_string_method = (
            'dashboard.templatetags.render_widget.render_to_string'
        )

    def get_mock_render_to_string_parameter(self, mock, parameter):
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

    def test_widget_is_registered(self):
        test_widget = CustomTestWidget()
        register_widget('test-widget', test_widget)
        self.assertEqual(get_widget('test-widget'), test_widget)

    def test_registering_twice_overrides_existing_widget(self):
        test_widget = CustomTestWidget()
        register_widget('test-widget', test_widget)
        test_widget_2 = CustomTestWidget()
        register_widget('test-widget', test_widget_2)
        self.assertEqual(get_widget('test-widget'), test_widget_2)

    def test_render_widget_loads_widget_type(self):
        test_widget = CustomTestWidget(context={'is_test_widget': True})
        register_widget('test-widget', test_widget)
        widget_instance = MockWidgetInstance('test-widget')
        with patch(self.render_to_string_method) as mock:
            render_widget(widget_instance)
            context = self.get_mock_render_to_string_parameter(mock, 'context')
        self.assertTrue(context['is_test_widget'])

    def test_render_widget_uses_template_name(self):
        test_widget = CustomTestWidget(template_name='test-widget-template')
        register_widget('test-widget', test_widget)
        widget_instance = MockWidgetInstance('test-widget')
        with patch(self.render_to_string_method) as mock:
            render_widget(widget_instance)
            template_name = self.get_mock_render_to_string_parameter(
                mock, 'template_name'
            )
        self.assertEqual(template_name, 'test-widget-template')

    def test_render_widget_calls_get_context_data(self):
        """ Test render widget calls get_context_data with the widget
            instance settings.
        """
        test_widget = CustomTestWidget()
        register_widget('test-widget', test_widget)
        widget_instance = MockWidgetInstance('test-widget', {'test': 'value'})
        with patch(self.render_to_string_method) as mock:
            render_widget(widget_instance)
            context = self.get_mock_render_to_string_parameter(mock, 'context')
        self.assertEqual(context['kwargs'], {'test': 'value'})

    def test_render_widget_without_get_ctx_data(self):
        """ Test render widget accepts widget types that do not implement
            get_context_data.
        """
        test_widget = CustomTestWidgetNoContextData()
        register_widget('test-widget', test_widget)
        widget_instance = MockWidgetInstance('test-widget')
        with patch(self.render_to_string_method) as mock:
            render_widget(widget_instance)
            context = self.get_mock_render_to_string_parameter(mock, 'context')
        self.assertEqual(context, {})

    def test_render_widget_without_template_name(self):
        """ Test render widget uses a default template when template_name
            is missing from the widget type object
        """
        test_widget = CustomTestWidgetNoTemplateName()
        register_widget('test-widget', test_widget)
        widget_instance = MockWidgetInstance('test-widget')
        with patch(self.render_to_string_method) as mock:
            render_widget(widget_instance)
            template_name = self.get_mock_render_to_string_parameter(
                mock, 'template_name'
            )
        self.assertEqual(
            template_name, 'dashboard/widget-error.html'
        )

    def test_render_widget_exception_includes_generic_message(self):
        """ Test that a widget which raises a generic exception will
            display a generic error message, not the content of the
            exception
        """
        test_widget = CustomTestWidgetRaisesException()
        register_widget('test-widget', test_widget)
        widget_instance = MockWidgetInstance('test-widget')
        with patch(self.render_to_string_method) as mock:
            render_widget(widget_instance)
            template_name = self.get_mock_render_to_string_parameter(
                mock, 'template_name'
            )
            context = self.get_mock_render_to_string_parameter(
                mock, 'context'
            )
        self.assertEqual(
            template_name, 'dashboard/widget-error.html'
        )
        self.assertEqual(
            context['error'], 'Widget error. See error logs.'
        )

    def test_render_widget_widgeterror_exception_includes_error_message(self):
        """ Test that a widget which raises a WidgetError exception will
            display the error message provided in the exception.
        """
        test_widget = CustomTestWidgetRaisesWidgetError()
        register_widget('test-widget', test_widget)
        widget_instance = MockWidgetInstance('test-widget')
        with patch(self.render_to_string_method) as mock:
            render_widget(widget_instance)
            template_name = self.get_mock_render_to_string_parameter(
                mock, 'template_name'
            )
            context = self.get_mock_render_to_string_parameter(
                mock, 'context'
            )
        self.assertEqual(
            template_name, 'dashboard/widget-error.html'
        )
        self.assertEqual(
            str(context['error']), 'message raised from get_context_data'
        )
