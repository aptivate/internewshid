# -*- coding: utf-8 -*-
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data_layer', '0012_auto_20181205_1417'),
    ]

    operations = [
        migrations.RenameField(
            model_name='message',
            old_name='ennumerator',
            new_name='enumerator',
        ),
    ]
