# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def create_initial_view_and_edit_page(apps, schema_editor):
    TabbedPage = apps.get_model("tabbed_page", "TabbedPage")
    TabInstance = apps.get_model("tabbed_page", "TabInstance")

    main, created = TabbedPage.objects.get_or_create(name='main')
    all_tab, created = TabInstance.objects.get_or_create(
        name='all',
        page=main,
        defaults={
            'tab_type': 'view-and-edit-table',
            'default': True,
            'position': 0,
            'label': 'All',
            'settings': {
                "columns": ["select_item", "created", "timestamp", "body"],
                "label": "All"
            }
        }
    )
    question_tab, created = TabInstance.objects.get_or_create(
        name='questions',
        page=main,
        defaults={
            'tab_type': 'view-and-edit-table',
            'default': False,
            'position': 1,
            'label': 'Questions',
            'settings': {
                'columns': ['select_item', 'created', 'timestamp', 'body',
                            'category'],
                'label': 'Questions',
                'collection_type': 'geopoll',
                'categories': ['ebola-questions'],
                'filters': {
                    'terms': ['item-types:question']
                }
            }
        }
    )
    rumours_tab, created = TabInstance.objects.get_or_create(
        name='rumors',
        page=main,
        defaults={
            'tab_type': 'view-and-edit-table',
            'default': False,
            'position': 1,
            'label': 'Rumors',
            'settings': {
                'columns': ['select_item', 'created', 'timestamp', 'body',
                            'network_provider'],
                'label': 'Rumors',
                'collection_type': 'rapidpro',
                'filters': {
                    'terms': ['item-types:rumor']
                }
            }
        }
    )


class Migration(migrations.Migration):

    dependencies = [
        ('hid', '0004_item_types'),
        ('tabbed_page', '0003_auto_20150807_1023')
    ]

    operations = [
        migrations.RunPython(create_initial_view_and_edit_page)
    ]
