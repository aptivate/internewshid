# -*- coding: utf-8 -*-
from django.db import migrations, models
import picklefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('data_layer', '0014_remove_message_feedback_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomConstance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=190, unique=True)),
                ('value', picklefield.fields.PickledObjectField(editable=False)),
            ],
            options={
                'db_table': 'constance_config',
                'verbose_name': 'constance',
                'verbose_name_plural': 'constances',
            },
        ),
    ]
