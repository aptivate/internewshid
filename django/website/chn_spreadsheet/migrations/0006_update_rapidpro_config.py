# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


RAPIDPRO_CONFIG = {
    "label": "rapidpro",
    "name": "RapidPro",
    "format": "excel",
    "type": "rumor",
    "columns": [
        {
            "name": "Phone",
            "type": "ignore",
            "field": "ignore"
        },
        {
            "name": "Name",
            "type": "ignore",
            "field": "ignore"
        },
        {
            "name": "Groups",
            "type": "ignore",
            "field": "ignore"
        },
        {
            "name": "Last Seen",
            "type": "date",
            "field": "timestamp",
            "date_format": "%m/%d/%y %H:%M:%S"
        },
        {
            "name": "Rumors (Text) - DEY Say sample flow",
            "type": "text",
            "field": "body"

        },
        {
            "name": "Channel",
            "type": "ignore",
            "field": "ignore"
        }
    ],
    "skip_header": 1
}


def update_rapidpro_config(apps, schema_editor):
    Profile = apps.get_model('chn_spreadsheet', 'SheetProfile')
    Profile.objects.filter(label='rapidpro').update(profile=RAPIDPRO_CONFIG)


class Migration(migrations.Migration):

    dependencies = [
        ('chn_spreadsheet', '0005_update_geopoll_config'),
    ]

    operations = [
        migrations.RunPython(update_rapidpro_config)
    ]
