# -*- coding: utf-8 -*-
from django.db import migrations


def remove_sheet_profiles(apps, schema_editor):
    SheetProfile = apps.get_model('chn_spreadsheet', 'SheetProfile')

    SheetProfile.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('chn_spreadsheet', '0012_auto_20181008_1321'),
    ]

    operations = [
        migrations.RunPython(remove_sheet_profiles)
    ]
