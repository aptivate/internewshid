from django.db import IntegrityError
from django.test import TestCase

from dashboard.models import Dashboard


class DashboardModelTestCase(TestCase):
    def setUp(self):
        dashboard = Dashboard.objects.create(name='dashboard1')
        dashboard.widgetinstance_set.create(widget_type='type1')
        dashboard.widgetinstance_set.create(widget_type='type2')
        self.dashboard = Dashboard.objects.get(pk=dashboard.id)

    def test_dashboard_has_expected_name(self):
        self.assertEqual(self.dashboard.name, 'dashboard1')

    def test_dashboard_has_expected_representation(self):
        self.assertEqual(str(self.dashboard), 'dashboard1')

    def test_dashboard_has_expected_widgets(self):
        widgets = self.dashboard.widgetinstance_set.all()
        self.assertEqual(len(widgets), 2)
        self.assertEqual(widgets[0].widget_type, 'type1')
        self.assertEqual(widgets[1].widget_type, 'type2')

    def test_dashboard_name_is_unique(self):
        Dashboard.objects.create(name='dashboard_x')
        with self.assertRaises(IntegrityError):
            Dashboard.objects.create(name='dashboard_x')
