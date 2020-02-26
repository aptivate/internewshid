# -*- coding: utf-8 -*-
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tabbed_page', '0002_auto_20150805_1521'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tabinstance',
            old_name='view_name',
            new_name='tab_type',
        ),
        migrations.AlterField(
            model_name='tabbedpage',
            name='name',
            field=models.SlugField(unique=True, max_length=128),
        ),
        migrations.AlterField(
            model_name='tabinstance',
            name='name',
            field=models.SlugField(max_length=128),
        ),
        migrations.AlterField(
            model_name='tabinstance',
            name='page',
            field=models.ForeignKey(related_name='tabs', to='tabbed_page.TabbedPage', on_delete=models.CASCADE),
        ),
    ]
