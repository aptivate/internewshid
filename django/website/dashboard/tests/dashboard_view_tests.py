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
        dashboard = Dashboard.objects.create(name='dashboard1')
        dashboard.widgetinstance_set.create(
            widget_type='test-widget-1',
            row=0,
            column=0
        )
        dashboard.widgetinstance_set.create(
            widget_type='test-widget-2',
            row=1,
            column=1
        )
        dashboard.widgetinstance_set.create(
            widget_type='test-widget-3',
            row=0,
            column=1
        )
        dashboard.widgetinstance_set.create(
            widget_type='test-widget-4',
            row=1,
            column=0
        )
        self.dashboard = Dashboard.objects.get(pk=dashboard.id)
        self.dashboard_view = DashboardView()
        self.view_args = {'name': 'dashboard1'}
        self.dashboard_view.kwargs = self.view_args

    def test_remove_duplicates(self):
        """ Ensure duplicates are removed and the order is kept"""
        test_array = [1, 2, 5, 1, 3, 2, 5, 3, 1, 4]
        self.assertEqual(
            self.dashboard_view._remove_duplicates(test_array),
            [1, 2, 5, 3, 4]
        )

    def test_context_data_includes_dashboard_name(self):
        context = self.dashboard_view.get_context_data(**self.view_args)
        self.assertEqual(context['name'], 'dashboard1')

    def test_context_data_includes_correct_number_of_rows(self):
        context = self.dashboard_view.get_context_data(**self.view_args)
        self.assertEqual(len(context['rows']), 2)

    def test_context_data_includes_correct_number_of_columns(self):
        context = self.dashboard_view.get_context_data(**self.view_args)
        self.assertEqual(len(context['rows'][0]), 2)
        self.assertEqual(len(context['rows'][1]), 2)

    def test_context_data_widgets_in_correct_order(self):
        context = self.dashboard_view.get_context_data(**self.view_args)
        rows = []
        rows.append([w.widget_type for w in context['rows'][0]])
        rows.append([w.widget_type for w in context['rows'][1]])
        self.assertEqual(rows, [
            ['test-widget-1', 'test-widget-3'],
            ['test-widget-4', 'test-widget-2']
        ])

    def test_context_data_includes_javascript(self):
        context = self.dashboard_view.get_context_data(**self.view_args)
        self.assertEqual(context['javascript'], [
            'file.js', 'app/file.js',
            'some.js', 'app2/file.js'
        ])

    def test_context_data_includes_css(self):
        context = self.dashboard_view.get_context_data(**self.view_args)
        self.assertEqual(context['css'], [
            'dashboard/dashboard.css',
            'file.css', 'app/file.css',
            'some.css', 'app2/file.css'
        ])
