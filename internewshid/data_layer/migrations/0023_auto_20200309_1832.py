# Generated by Django 2.2.11 on 2020-03-09 12:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data_layer', '0022_remove_message_source'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customconstance',
            options={'managed': False, 'verbose_name': 'constance', 'verbose_name_plural': 'constances'},
        ),
    ]