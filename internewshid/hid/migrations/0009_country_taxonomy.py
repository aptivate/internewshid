# -*- coding: utf-8 -*-
from django.db import migrations

TERMS = (
    ('Liberia', 'Liberia'),
)


def create_taxonomy(apps, schema_editor):
    Taxonomy = apps.get_model('taxonomies', 'Taxonomy')
    Term = apps.get_model('taxonomies', 'Term')
    taxonomy = Taxonomy(
        name='Countries',
        slug='countries',
    )
    taxonomy.save()

    terms = [
        Term(name=t[0], long_name=t[1], taxonomy=taxonomy)
        for t in TERMS
    ]

    Term.objects.bulk_create(terms)


class Migration(migrations.Migration):

    dependencies = [
        ('hid', '0008_origin_taxonomy'),
        ('taxonomies', '0004_taxonomy_vocabulary'),
    ]

    operations = [
        migrations.RunPython(create_taxonomy)
    ]
