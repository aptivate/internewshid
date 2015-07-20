from django.test import TestCase
from dashboard.models import WidgetInstance, Dashboard


class WidgetInstanceModelTestCase(TestCase):
    def setUp(self):
        dashboard = Dashboard.objects.create(name='dashboard1')
        self.dashboard = Dashboard.objects.get(pk=dashboard.id)
        instance = WidgetInstance.objects.create(
            widget_type='type1',
            dashboard=self.dashboard,
            row=0,
            column=0,
            width=12,
            height='medium',
            settings={
                'key1': 'value1',
                'key2': 'value2'
            }
        )
        self.instance = WidgetInstance.objects.get(pk=instance.id)

    def test_instance_has_expected_name(self):
        self.assertEqual(self.instance.widget_type, 'type1')

    def test_instance_has_expected_representation(self):
        self.assertEqual(str(self.instance), 'Instance of type1')

    def test_instance_has_expected_settings(self):
        # Note that it is not our job to test how this
        # is serialized - we just ensure the settings
        # are available.
        self.assertEqual(self.instance.settings, {
            'key1': 'value1',
            'key2': 'value2'
        })
