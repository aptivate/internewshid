# -*- coding: utf-8 -*-
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_layer', '0019_message_sub_location'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='collection_type',
            field=models.CharField(blank=True, max_length=190),
        ),
    ]
