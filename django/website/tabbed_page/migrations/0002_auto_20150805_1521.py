# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('tabbed_page', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TabInstance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('settings', jsonfield.fields.JSONField(blank=True)),
                ('view_name', models.CharField(max_length=128)),
                ('name', models.CharField(max_length=128)),
                ('default', models.BooleanField(default=False)),
                ('position', models.PositiveIntegerField(default=0)),
                ('label', models.CharField(max_length=128)),
                ('page', models.ForeignKey(to='tabbed_page.TabbedPage')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='tab',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='tab',
            name='page',
        ),
        migrations.DeleteModel(
            name='Tab',
        ),
        migrations.AlterUniqueTogether(
            name='tabinstance',
            unique_together=set([('name', 'page')]),
        ),
    ]
