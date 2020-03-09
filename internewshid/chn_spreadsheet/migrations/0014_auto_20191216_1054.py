# -*- coding: utf-8 -*-
from django.db import migrations


def migrate_source_columns_to_collection_type(apps, schema_editor):
    SheetProfile = apps.get_model('chn_spreadsheet', 'SheetProfile')
    for sheet_profile in SheetProfile.objects.all():
        migrated_columns = []

        for column in sheet_profile.profile['columns']:
            if 'field' in column and column['field'] == 'source':
                column['field'] = 'collection_type'
            if 'name' in column and column['name'] == 'Source':
                column['name'] = 'Collection Type'
            migrated_columns.append(column)

        sheet_profile.profile['columns'] = migrated_columns
        sheet_profile.save()


class Migration(migrations.Migration):

    dependencies = [
        ('chn_spreadsheet', '0013_auto_20181019_1607'),
    ]

    operations = [
        migrations.RunPython(migrate_source_columns_to_collection_type),
    ]
