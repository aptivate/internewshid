# -*- coding: utf-8 -*-
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
