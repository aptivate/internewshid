# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-12-05 14:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_layer', '0011_message_feedback_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='feedback_type',
            field=models.CharField(blank=True, choices=[(b'CONCERN', b'Concern'), (b'QUESTION', b'Question'), (b'RUMOUR', b'Rumour')], max_length=100),
        ),
    ]