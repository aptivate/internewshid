# -*- coding: utf-8 -*-
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_layer', '0015_customconstance'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='internal_id',
            field=models.CharField(blank=True, max_length=80),
        ),
    ]
