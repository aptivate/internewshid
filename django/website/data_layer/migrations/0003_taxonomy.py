# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data_layer', '0002_auto_20150619_2132'),
    ]

    operations = [
        migrations.CreateModel(
            name='Taxonomy',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='Taxonomy Name', unique=True, max_length=250, verbose_name='Name', db_index=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
