# -*- coding: utf-8 -*-
from django.db import migrations


def remove_widget_instances(apps, schema_editor):
    WidgetInstance = apps.get_model('dashboard', 'WidgetInstance')

    WidgetInstance.objects.all().delete()


def remove_tabbed_pages(apps, schema_editor):
    TabbedPage = apps.get_model('tabbed_page', 'TabbedPage')

    TabbedPage.objects.all().delete()


def remove_tab_instances(apps, schema_editor):
    TabInstance = apps.get_model('tabbed_page', 'TabInstance')

    TabInstance.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('hid', '0011_remove_ebola_questions'),
    ]

    operations = [
        migrations.RunPython(remove_widget_instances),
        migrations.RunPython(remove_tabbed_pages),
        migrations.RunPython(remove_tab_instances)
    ]
