# -*- coding: utf-8 -*-
from django.db import migrations


GEOPOLL_CONFIG = {
    "label": "geopoll",
    "name": "Geopoll",
    "format": "excel",
    "type": "question",
    "columns": [
        {
            "name": "Province",
            "type": "ignore",
            "field": "ignore"
        },
        {
            "name": "CreatedDate",
            "type": "date",
            "field": "timestamp",
            "date_format": "%m/%d/%y"
        },
        {
            "name": "AgeGroup",
            "type": "ignore",
            "field": "ignore"
        },
        {
            "name": "QuestIO",
            "type": "text",
            "field": "body"
        }
    ],
    "skip_header": 1
}


def update_geopoll_config(apps, schema_editor):
    Profile = apps.get_model('chn_spreadsheet', 'SheetProfile')
    Profile.objects.filter(label='geopoll').update(
        profile=GEOPOLL_CONFIG)


class Migration(migrations.Migration):

    dependencies = [
        ('chn_spreadsheet', '0004_add_rapidpro_config'),
    ]

    operations = [
        migrations.RunPython(update_geopoll_config)
    ]
