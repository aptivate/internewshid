# -*- coding: utf-8 -*-
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Taxonomy',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='Taxonomy Name', unique=True, max_length=190, verbose_name='Name', db_index=True)),
                ('slug', models.SlugField(unique=True, max_length=190, verbose_name='Slug')),
            ],
        ),
        migrations.CreateModel(
            name='Term',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='Tag or Category Name', unique=True, max_length=190, verbose_name='Name', db_index=True)),
                ('long_name', models.TextField(verbose_name='Long Name', blank=True)),
                ('taxonomy', models.ForeignKey(
                    related_name='taxonomies_term_term', verbose_name='Taxonomy', to='taxonomies.Taxonomy', on_delete=models.CASCADE)),
            ],
        ),
    ]
