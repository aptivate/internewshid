# -*- coding: utf-8 -*-
from django.db import migrations


def migrate_source_filter_to_collection_type(apps, schema_editor):
    TabbedPage = apps.get_model('tabbed_page', 'TabbedPage')
    for tabbed_page in TabbedPage.objects.all():
        for tab in tabbed_page.tabs.all():
            filters = tab.settings['dynamic_filters']
            migrated_filters = [
                f if f != 'source' else 'collection_type'
                for f in filters
            ]
            tab.settings['dynamic_filters'] = migrated_filters
            tab.save()
        tabbed_page.save()


class Migration(migrations.Migration):

    dependencies = [
        ('tabbed_page', '0003_auto_20150807_1023'),
    ]

    operations = [
        migrations.RunPython(migrate_source_filter_to_collection_type),
    ]
