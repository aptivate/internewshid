# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def rename_question_type_terms(apps, schema_editor):
    Term = apps.get_model('taxonomies', 'Term')

    old_question_names = (
        "Vaccine",
        "Measures",
        "Symptoms",
        "Stigmatism",
        "Victims",
        "Schools",
        "Updates",
        "Origin",
        "Others",
        "Real",
    )

    new_question_types = (
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

    rename_map = map(
        lambda *args: tuple(args),
        old_question_names,
        new_question_types,
    ) # zip, but with None for missing new questions

    for (old_name, new_question) in rename_map:
        term = Term.objects.get(name=old_name)
        if new_question:
            new_name, new_long_name = new_question
            term = Term.objects.get(name=old_name)
            term.name = new_name
            term.long_name = new_long_name
            term.save()
        else:
            term.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('hid', '0001_question_types'),
    ]

    operations = [
        migrations.RunPython(rename_question_type_terms)
    ]
