# -*- coding: utf-8 -*-
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data_layer', '0016_message_internal_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='message',
            old_name='internal_id',
            new_name='external_id',
        ),
    ]
