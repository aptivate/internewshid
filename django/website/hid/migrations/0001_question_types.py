# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def create_question_types(apps, schema_editor):
    Taxonomy = apps.get_model('taxonomies', 'Taxonomy')
    taxonomy = Taxonomy(name="Ebola Questions", slug="ebola-questions")
    taxonomy.save()

    question_types = (
        ("Vaccine", "Vaccine Trial"),
        ("Measures", "What measures could end Ebola?"),
        ("Symptoms", "Symptoms/Medical"),
        ("Stigmatism", "Are survivors stigmatized?"),
        ("Victims", "Number of Victims?"),
        ("Schools", "Does Ebola affect schools?"),
        ("Updates", "Are there updates on Ebola?"),
        ("Origin", "What is the origin of Ebola?"),
        ("Others", "Others"),
        ("Real", "Is Ebola real?"),
    )

    Term = apps.get_model('taxonomies', 'Term')
    new_terms = [Term(
        name=qt[0],
        long_name=qt[1],
        taxonomy=taxonomy) for qt in question_types]

    db_alias = schema_editor.connection.alias
    Term.objects.using(db_alias).bulk_create(new_terms)


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.RunPython(create_question_types)
    ]
