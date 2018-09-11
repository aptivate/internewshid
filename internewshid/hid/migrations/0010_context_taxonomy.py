# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


TERMS = (
    ('Ebola-Liberia', 'Ebola-Liberia'),
)


def create_taxonomy(apps, schema_editor):
    Taxonomy = apps.get_model('taxonomies', 'Taxonomy')
    Term = apps.get_model('taxonomies', 'Term')
    taxonomy = Taxonomy(
        name='Contexts',
        slug='contexts',
    )
    taxonomy.save()

    terms = [
        Term(name=t[0], long_name=t[1], taxonomy=taxonomy)
        for t in TERMS
    ]

    Term.objects.bulk_create(terms)


class Migration(migrations.Migration):

    dependencies = [
        ('hid', '0009_country_taxonomy'),
        ('taxonomies', '0004_taxonomy_vocabulary'),
    ]

    operations = [
        migrations.RunPython(create_taxonomy)
    ]
