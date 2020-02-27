# -*- coding: utf-8 -*-
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_layer', '0006_message_network_provider'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='translation',
            field=models.TextField(blank=True),
        ),
    ]
