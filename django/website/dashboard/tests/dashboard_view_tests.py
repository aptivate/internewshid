from django.test import TestCase

from dashboard.models import Dashboard
from dashboard.views import DashboardView
from dashboard.widget_pool import register_widget


class TestWidget(object):
    """ A test widget with a template name and an implementation of
        of get_context_data
    """
    template_name = 'test-widget-template'
    javascript = []
    css = []

    def __init__(self, javascript=None, css=None):
        if javascript is not None:
            self.javascript = javascript
        if css is not None:
            self.css = css

    def get_context_data(self, **kwargs):
        return {
            'is_test_widget': True,
            'value': kwargs['setting']
        }


class TestDashboardView(TestCase):
    def setUp(self):
        """ Register a number of widget types we can use for
            out tests
        """
        register_widget('test-widget-1', TestWidget(
            ['file.js', 'app/file.js'],
            ['file.css', 'app/file.css']
        ))
        register_widget('test-widget-2', TestWidget(
            ['some.js', 'file.js', 'app2/file.js'],
            ['some.css', 'file.css', 'app2/file.css']
        ))
        register_widget('test-widget-3', TestWidget())
        register_widget('test-widget-4', TestWidget())

    def setup_dashboard(self, name, widgets=None):
        """ Helper function to setup a dashboard."""
        dashboard = Dashboard.objects.create(name='dashboard1')
        if widgets is None:
            widgets = []
        for widget in widgets:
            dashboard.widgetinstance_set.create(
                widget_type=widget['widget_type'],
                row=widget['row'],
                column=widget['column']
            )
        return dashboard

    def get_dashboard_view_context(self, name):
        """ Helper function to create a dashboard view and invoke
            it's get_context_data method
        """
        dashboard_view = DashboardView()
        view_args = {'name': 'dashboard1'}
        dashboard_view.kwargs = view_args
        return dashboard_view.get_context_data(**view_args)

    def test_remove_duplicates(self):
        """ Ensure duplicates are removed and the order is kept"""
        dashboard_view = DashboardView()
        test_array = [1, 2, 5, 1, 3, 2, 5, 3, 1, 4]
        self.assertEqual(
            dashboard_view._remove_duplicates(test_array),
            [1, 2, 5, 3, 4]
        )

    def test_context_data_includes_dashboard_name(self):
        self.setup_dashboard('dashboard1')
        context = self.get_dashboard_view_context('dashboard1')
        self.assertEqual(context['name'], 'dashboard1')

    def test_context_data_includes_correct_number_of_rows(self):
        self.setup_dashboard('dashboard1', [
            {
                'widget_type': 'test-widget-1',
                'row': 0,
                'column': 0
            },
            {
                'widget_type': 'test-widget-2',
                'row': 1,
                'column': 0
            }
        ])
        context = self.get_dashboard_view_context('dashboard1')
        self.assertEqual(len(context['rows']), 2)

    def test_context_data_includes_correct_number_of_columns(self):
        self.setup_dashboard('dashboard1', [
            {
                'widget_type': 'test-widget-1',
                'row': 0,
                'column': 0
            },
            {
                'widget_type': 'test-widget-2',
                'row': 0,
                'column': 1
            }
        ])
        context = self.get_dashboard_view_context('dashboard1')
        self.assertEqual(len(context['rows'][0]), 2)

    def test_context_data_widgets_in_correct_order(self):
        self.setup_dashboard('dashboard1', [
            {
                'widget_type': 'test-widget-1',
                'row': 0,
                'column': 0
            },
            {
                'widget_type': 'test-widget-2',
                'row': 1,
                'column': 1
            },
            {
                'widget_type': 'test-widget-3',
                'row': 0,
                'column': 1
            },
            {
                'widget_type': 'test-widget-4',
                'row': 1,
                'column': 0
            }
        ])
        context = self.get_dashboard_view_context('dashboard1')
        rows = []
        rows.append([w.widget_type for w in context['rows'][0]])
        rows.append([w.widget_type for w in context['rows'][1]])
        self.assertEqual(rows, [
            ['test-widget-1', 'test-widget-3'],
            ['test-widget-4', 'test-widget-2']
        ])

    def test_context_data_includes_javascript(self):
        self.setup_dashboard('dashboard1', [
            {
                'widget_type': 'test-widget-1',
                'row': 0,
                'column': 0
            },
            {
                'widget_type': 'test-widget-2',
                'row': 0,
                'column': 1
            }
        ])
        context = self.get_dashboard_view_context('dashboard1')
        self.assertEqual(context['javascript'], [
            'file.js', 'app/file.js',
            'some.js', 'app2/file.js'
        ])

    def test_context_data_includes_css(self):
        self.setup_dashboard('dashboard1', [
            {
                'widget_type': 'test-widget-1',
                'row': 0,
                'column': 0
            },
            {
                'widget_type': 'test-widget-2',
                'row': 0,
                'column': 1
            }
        ])
        context = self.get_dashboard_view_context('dashboard1')
        self.assertEqual(context['css'], [
            'dashboard/dashboard.css',
            'file.css', 'app/file.css',
            'some.css', 'app2/file.css'
        ])
