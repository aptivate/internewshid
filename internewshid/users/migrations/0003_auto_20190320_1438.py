# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2019-03-20 14:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20150820_1634'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='business_email',
            field=models.EmailField(max_length=190, unique=True, verbose_name=b'Email'),
        ),
    ]
