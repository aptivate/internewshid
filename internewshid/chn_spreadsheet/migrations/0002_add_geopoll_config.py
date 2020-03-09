# -*- coding: utf-8 -*-
from django.db import migrations


GEOPOLL_CONFIG = {
    "label": "geopoll",
    "name": "Geopoll",
    "format": "excel",
    "type": "message",
    "columns": [
        {
            "name": "Province",
            "type": "text",
            "field": "message.location"
        },
        {
            "name": "CreatedDate",
            "type": "date",
            "field": "message.created"
        },
        {
            "name": "AgeGroup",
            "type": "text",
            "field": "message.age"
        },
        {
            "name": "QuestIO",
            "type": "text",
            "field": "message.content"
        }
    ],
    "skip_header": 1
}


def add_geopoll_config(apps, schema_editor):
    Profile = apps.get_model('chn_spreadsheet', 'SheetProfile')
    Profile.objects.create(label='geopoll', profile=GEOPOLL_CONFIG)


class Migration(migrations.Migration):

    dependencies = [
        ('chn_spreadsheet', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_geopoll_config)
    ]
