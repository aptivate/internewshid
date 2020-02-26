# -*- coding: utf-8 -*-
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0002_auto_20150709_1244'),
    ]

    operations = [
        migrations.AddField(
            model_name='widgetinstance',
            name='height',
            field=models.CharField(default='medium', max_length=6, choices=[('small', 'Small'), ('medium', 'Medium'), ('tall', 'Tall')]),
        ),
    ]
