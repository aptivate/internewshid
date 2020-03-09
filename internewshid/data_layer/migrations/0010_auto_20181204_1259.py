# -*- coding: utf-8 -*-
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_layer', '0009_message_location'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='age',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='message',
            name='ennumerator',
            field=models.CharField(blank=True, max_length=190),
        ),
        migrations.AddField(
            model_name='message',
            name='gender',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='message',
            name='source',
            field=models.CharField(blank=True, max_length=190),
        ),
    ]
