# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Dashboard',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='WidgetInstance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('widget_type', models.CharField(max_length=128)),
                ('row', models.PositiveIntegerField(default=0)),
                ('column', models.PositiveIntegerField(default=0, validators=[django.core.validators.MaxValueValidator(11, b'column must be between 0 and 11')])),
                ('width', models.PositiveIntegerField(default=12, validators=[django.core.validators.MinValueValidator(1, b'width must be between 1 and 12'), django.core.validators.MaxValueValidator(12, b'width must be between 1 and 12')])),
                ('settings', jsonfield.fields.JSONField(blank=True)),
                ('dashboard', models.ForeignKey(to='dashboard.Dashboard')),
            ],
        ),
    ]
