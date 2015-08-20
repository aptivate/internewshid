# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('taxonomies', '0003_taxonomy_multiplicity'),
    ]

    operations = [
        migrations.AddField(
            model_name='taxonomy',
            name='vocabulary',
            field=models.CharField(default=b'closed', max_length=30, choices=[(b'fixed', 'Not modifiable by any user, system only'), (b'closed', 'Only admin users who have permission to define and edit taxonomies'), (b'open', 'Any user who has permission to use taxonomies')]),
        ),
    ]
