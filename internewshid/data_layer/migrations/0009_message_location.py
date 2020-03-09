# -*- coding: utf-8 -*-
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
