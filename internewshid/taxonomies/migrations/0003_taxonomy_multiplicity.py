# -*- coding: utf-8 -*-
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('taxonomies', '0002_auto_20150716_2018'),
    ]

    operations = [
        migrations.AddField(
            model_name='taxonomy',
            name='multiplicity',
            field=models.CharField(default=b'optional', max_length=30, choices=[(b'optional', 'Zero or One'), (b'multiple', 'Zero or More')]),
        ),
    ]
