# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-10-19 10:55
from __future__ import unicode_literals

from django.db import migrations


def remove_ebola_questions(apps, schema_editor):
    Taxonomy = apps.get_model('taxonomies', 'Taxonomy')

    taxonomy = Taxonomy.objects.get(slug='ebola-questions')
    taxonomy.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('hid', '0010_context_taxonomy'),
    ]

    operations = [
        migrations.RunPython(remove_ebola_questions)
    ]
