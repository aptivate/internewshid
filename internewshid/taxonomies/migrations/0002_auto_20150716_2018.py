# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('taxonomies', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='term',
            name='name',
            field=models.CharField(help_text='Tag or Category Name', max_length=190, verbose_name='Name', db_index=True),
        ),
        migrations.AlterUniqueTogether(
            name='term',
            unique_together=set([('name', 'taxonomy')]),
        ),
        migrations.AlterIndexTogether(
            name='term',
            index_together=set([('name', 'taxonomy')]),
        ),
    ]
