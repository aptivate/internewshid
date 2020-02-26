# -*- coding:  utf-8 -*-
from django.db import migrations


KOBO_CONFIG = {
  "label":  "kobo",
  "name":  "Kobo",
  "format":  "excel",
  "skip_header":  1,
  "taxonomies": {},
  "columns":  [
    {
      "name":  "start",
      "field": "timestamp",
      "type": "date",
      "date_format": "%Y-%m-%dT%H: %M: %S.%f%z"
    },
    {
      "name": "end",
      "field": "ignore",
      "type": "ignore"
    },
    {
      "name": "username",
      "field": "ignore",
      "type": "ignore"
    },
    {
      "name": "What is the feedback or rumour?",
      "field": "body",
      "type": "text"
    },
    {
      "name": "What is the feedback or rumour translation?",
      "field": "translation",
      "type": "text"
    },
    {
      "name": "date",
      "field": "ignore",
      "type": "ignore",
    },
    {
      "name": "gender",
      "field": "terms",
      "type": "taxonomy",
      "taxonomy": "tags"
    },
    {
      "name": "Age",
      "field": "ignore",
      "type": "ignore"
    },
    {
      "name": "Location",
      "field": "location",
      "type": "text",
    },
    {
      "name": "comment",
      "field": "ignore",
      "type": "ignore"
    },
    {
      "name": "_id",
      "field": "ignore",
      "type": "ignore"
    },
    {
      "name": "_uuid",
      "field": "ignore",
      "type": "ignore"
    },
    {
      "name": "_submission_time",
      "field": "ignore",
      "type": "ignore"
    },
    {
      "name": "_index",
      "field": "ignore",
      "type": "ignore"
    }
  ]
}


def add_kobo_config(apps, schema_editor):
    """Add the Kobo SpreadSheet Profile."""
    Profile = apps.get_model('chn_spreadsheet', 'SheetProfile')
    kobo_profile = Profile.objects.filter(label='kobo')
    if kobo_profile.exists():
        return kobo_profile.update(profile=KOBO_CONFIG)
    return Profile.objects.create(label='kobo', profile=KOBO_CONFIG)


class Migration(migrations.Migration):

    dependencies = [
        ('chn_spreadsheet', '0011_update_geopoll_config'),
    ]

    operations = [
        migrations.RunPython(add_kobo_config)
    ]
