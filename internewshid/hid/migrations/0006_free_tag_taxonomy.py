# -*- coding: utf-8 -*-
from django.db import migrations


def create_taxonomy(apps, schema_editor):
    Taxonomy = apps.get_model('taxonomies', 'Taxonomy')
    taxonomy = Taxonomy(
        name='Tags',
        slug='tags',
        multiplicity='multiple')
    taxonomy.save()


class Migration(migrations.Migration):

    dependencies = [
        ('hid', '0005_initial_tabbed_page'),
        ('taxonomies', '0003_taxonomy_multiplicity'),
    ]

    operations = [
        migrations.RunPython(create_taxonomy)
    ]
