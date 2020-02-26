# -*- coding: utf-8 -*-
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20150820_1634'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='business_email',
            field=models.EmailField(max_length=190, unique=True, verbose_name=b'Email'),
        ),
    ]
