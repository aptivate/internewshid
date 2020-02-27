# -*- coding: utf-8 -*-
from django.db import migrations


def migrate_source_to_collection_type(apps, schema_editor):
    Message = apps.get_model('data_layer', 'Message')
    for message in Message.objects.all():
        if hasattr(message, 'source'):
            message.collection_type = message.source
            message.save()


class Migration(migrations.Migration):

    dependencies = [
        ('data_layer', '0020_message_collection_type'),
    ]

    operations = [
        migrations.RunPython(migrate_source_to_collection_type),
    ]
