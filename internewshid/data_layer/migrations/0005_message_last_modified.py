# -*- coding: utf-8 -*-
from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('data_layer', '0004_auto_20150720_1723'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='last_modified',
            field=models.DateTimeField(default=datetime.datetime(2015, 7, 29, 11, 25, 40, 915975, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
    ]
