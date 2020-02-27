# -*- coding: utf-8 -*-
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('taxonomies', '0001_initial'),
        ('data_layer', '0002_auto_20150619_2132'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='terms',
            field=models.ManyToManyField(to='taxonomies.Term'),
        ),
    ]
