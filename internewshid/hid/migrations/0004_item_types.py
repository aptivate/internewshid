# -*- coding: utf-8 -*-
from django.db import migrations


def create_item_types(apps, schema_editor):
    Taxonomy = apps.get_model('taxonomies', 'Taxonomy')
    taxonomy = Taxonomy(name="Item Types", slug="item-types")
    taxonomy.save()

    item_types = (
        ("question", "Question"),
        ("rumor", "Rumor"),
    )

    Term = apps.get_model('taxonomies', 'Term')
    new_terms = [Term(
        name=name,
        long_name=long_name,
        taxonomy=taxonomy) for name, long_name in item_types]

    db_alias = schema_editor.connection.alias
    Term.objects.using(db_alias).bulk_create(new_terms)


class Migration(migrations.Migration):

    dependencies = [
        ('hid', '0003_rename_question_type_terms'),
        ('taxonomies', '0002_auto_20150716_2018')
    ]

    operations = [
        migrations.RunPython(create_item_types)
    ]
