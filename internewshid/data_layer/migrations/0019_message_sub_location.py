# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2019-12-09 04:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_layer', '0018_auto_20190530_2152'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='sub_location',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
