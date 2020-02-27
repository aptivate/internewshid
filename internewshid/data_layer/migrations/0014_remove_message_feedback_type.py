# -*- coding: utf-8 -*-
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data_layer', '0013_auto_20181213_1153'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='feedback_type',
        ),
    ]
