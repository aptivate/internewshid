# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def create_sample_widgets(apps, schema_editor):
    Dashboard = apps.get_model('dashboard', 'Dashboard')
    WidgetInstance = apps.get_model('dashboard', 'WidgetInstance')
    main = Dashboard.objects.get(name='main')

    WidgetInstance.objects.create(
        dashboard=main,
        widget_type='basic-text-widget',
        row=0,
        column=0,
        width=6,
        height='small',
        settings={
            'title': 'Sample title',
            'text': 'Sample text'
        }
    )
    WidgetInstance.objects.create(
        dashboard=main,
        widget_type='basic-text-widget',
        row=0,
        column=1,
        width=6,
        height='small',
        settings={
            'title': 'Another title',
            'text': 'Another text'
        }
    )
    WidgetInstance.objects.create(
        dashboard=main,
        widget_type='basic-text-widget',
        row=1,
        column=1,
        width=6,
        height='medium',
        settings={
            'title': 'Yes antoher widget title',
            'text': 'Yet another text'
        }
    )
    WidgetInstance.objects.create(
        dashboard=main,
        widget_type='question-chart-widget',
        row=1,
        column=0,
        width=6,
        height='medium',
        settings={
            'name': 'a chart',
            'questions': {
                'question three': 23,
                'question one': 10,
                'question four': 150,
                'question two': 50
            }
        }
    )


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0003_widgetinstance_height')
    ]

    operations = [
        migrations.RunPython(create_sample_widgets)
    ]
