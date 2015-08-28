# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


RAPIDPRO_CONFIG = {
    "label": "rapidpro",
    "name": "RapidPro",
    "format": "excel",
    "taxonomies": {
        "item-types": "rumor",
        "data-origins": "Rapidpro Spreadsheet",
        "countries": "Liberia",
        "contexts": "Ebola-Liberia",
    },
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
            "type": "text",
            "field": "network_provider"
        },
        {
            "name": "Region",
            "type": "taxonomy",
            "field": "terms",
            "taxonomy": "tags"
        }
    ],
    "skip_header": 1
}


def update_rapidpro_config(apps, schema_editor):
    Profile = apps.get_model('chn_spreadsheet', 'SheetProfile')
    Profile.objects.filter(label='rapidpro').update(profile=RAPIDPRO_CONFIG)


class Migration(migrations.Migration):

    dependencies = [
        ('chn_spreadsheet', '0009_update_rapidpro_config'),
        ('hid', '0010_context_taxonomy'),
    ]

    operations = [
        migrations.RunPython(update_rapidpro_config)
    ]
