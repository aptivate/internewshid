# Generated by Django 2.2.11 on 2020-03-09 12:32

import collections
from django.db import migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('chn_spreadsheet', '0014_auto_20191216_1054'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sheetprofile',
            name='profile',
            field=jsonfield.fields.JSONField(load_kwargs={'object_pairs_hook': collections.OrderedDict}),
        ),
    ]