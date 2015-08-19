# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data_layer', '0005_message_last_modified'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='network_provider',
            field=models.CharField(max_length=200, blank=True),
        ),
    ]
