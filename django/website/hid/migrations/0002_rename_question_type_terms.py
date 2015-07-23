# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

QUESTION_TYPES = (
    ('Ebola updates', 'What are the current updates on Ebola?'),
    ('Ebola authenticity', 'Is Ebola a real disease?'),
    ('Ebola prevention', 'What measures could be put in place to end Ebola?'),
    ('Ebola origins', 'What is the origin of Ebola?'),
    ('Non-Ebola concerns', 'What are the non-Ebola related concerns?'),
    ('Ebola symptons', 'What are the symptoms of Ebola?'),
    ('Ebola vaccine', 'What are the stakes of the Ebola vaccine?'),
    ('Liberia Ebola-free', 'Can Liberia be Ebola free?'),
    ('Unknown', 'Unknown.'),
)

def rename_question_type_terms(apps, schema_editor):
    Taxonomy = apps.get_model('taxonomies', 'Taxonomy')
    Term = apps.get_model('taxonomies', 'Term')
    (taxonomy, _) = Taxonomy.objects.get_or_create(
        slug="ebola-questions",
        name="Ebola Questions",
    )
    Term.objects.filter(taxonomy=taxonomy).delete()
    new_terms = [
        Term(name=qt[0], long_name=qt[1], taxonomy=taxonomy)
        for qt in QUESTION_TYPES
    ]

    Term.objects.bulk_create(new_terms)


class Migration(migrations.Migration):

    dependencies = [
        ('hid', '0001_question_types'),
    ]

    operations = [
        migrations.RunPython(rename_question_type_terms)
    ]
