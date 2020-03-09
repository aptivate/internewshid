# -*- coding: utf-8 -*-
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data_layer', '0021_auto_20191216_1007'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='source',
        ),
    ]
