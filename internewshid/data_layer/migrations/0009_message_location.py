# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-10-16 11:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_layer', '0008_auto_20181011_1149'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='location',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
