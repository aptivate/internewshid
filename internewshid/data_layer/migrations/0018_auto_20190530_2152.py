# -*- coding: utf-8 -*-
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data_layer', '0017_auto_20190523_2245'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='message',
            options={'permissions': (('can_change_message_body', 'Can change feedback'),)},
        ),
    ]
