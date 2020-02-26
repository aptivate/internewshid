# -*- coding: utf-8 -*-
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_layer', '0010_auto_20181204_1259'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='feedback_type',
            field=models.CharField(blank=True, choices=[(b'CONCERN', b'Concern'), (b'QUESTION', b'Question'), (b'RUMOUR', b'Rumour')], default=None, max_length=100),
        ),
    ]
