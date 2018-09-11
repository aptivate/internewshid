# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data_layer', '0003_message_terms'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='terms',
            field=models.ManyToManyField(related_name='items', to='taxonomies.Term'),
        ),
    ]
