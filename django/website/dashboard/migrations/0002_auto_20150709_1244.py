from __future__ import unicode_literals

from django.db import migrations


def create_main_dashboard(apps, schema_editor):
    Dashboard = apps.get_model('dashboard', 'Dashboard')
    Dashboard.objects.create(name='main')


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_main_dashboard)
    ]
