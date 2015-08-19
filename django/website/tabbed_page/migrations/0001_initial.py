# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Tab',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('settings', jsonfield.fields.JSONField(blank=True)),
                ('view_name', models.CharField(max_length=128)),
                ('name', models.CharField(max_length=128)),
                ('default', models.BooleanField(default=False)),
                ('position', models.PositiveIntegerField(default=0)),
                ('label', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='TabbedPage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=128)),
            ],
        ),
        migrations.AddField(
            model_name='tab',
            name='page',
            field=models.ForeignKey(to='tabbed_page.TabbedPage'),
        ),
        migrations.AlterUniqueTogether(
            name='tab',
            unique_together=set([('name', 'page')]),
        ),
    ]
