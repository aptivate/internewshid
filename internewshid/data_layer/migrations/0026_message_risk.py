# Generated by Django 2.2.11 on 2020-03-25 15:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_layer', '0025_message_language'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='risk',
            field=models.CharField(blank=True, max_length=30),
        ),
    ]