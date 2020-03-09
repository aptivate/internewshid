# -*- coding: utf-8 -*-
from django.db import migrations

TERMS = (
    ('Geopoll Spreadsheet', 'Geopoll Spreadsheet'),
    ('Rapidpro Spreadsheet', 'Rapidpro Spreadsheet'),
    ('Form Entry', 'Form Entry'),
)


def create_taxonomy(apps, schema_editor):
    Taxonomy = apps.get_model('taxonomies', 'Taxonomy')
    Term = apps.get_model('taxonomies', 'Term')
    taxonomy = Taxonomy(
        name='Data Origins',
        slug='data-origins',
    )
    taxonomy.save()

    terms = [
        Term(name=t[0], long_name=t[1], taxonomy=taxonomy)
        for t in TERMS
    ]

    Term.objects.bulk_create(terms)


class Migration(migrations.Migration):

    dependencies = [
        ('hid', '0007_free_tag_vocabulary'),
        ('taxonomies', '0004_taxonomy_vocabulary'),
    ]

    operations = [
        migrations.RunPython(create_taxonomy)
    ]
