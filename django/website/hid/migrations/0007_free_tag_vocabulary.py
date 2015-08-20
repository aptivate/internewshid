# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def update_taxonomy(apps, schema_editor):
    Taxonomy = apps.get_model('taxonomies', 'Taxonomy')
    taxonomy = Taxonomy.objects.get(slug='tags')
    taxonomy.vocabulary = 'open'
    taxonomy.save()


class Migration(migrations.Migration):

    dependencies = [
        ('hid', '0006_free_tag_taxonomy'),
        ('taxonomies', '0004_taxonomy_vocabulary'),
    ]

    operations = [
        migrations.RunPython(update_taxonomy)
    ]
