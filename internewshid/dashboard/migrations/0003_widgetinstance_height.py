# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0002_auto_20150709_1244'),
    ]

    operations = [
        migrations.AddField(
            model_name='widgetinstance',
            name='height',
            field=models.CharField(default=b'medium', max_length=6, choices=[(b'small', b'Small'), (b'medium', b'Medium'), (b'tall', b'Tall')]),
        ),
    ]
