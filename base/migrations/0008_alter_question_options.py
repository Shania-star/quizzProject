# Generated by Django 4.1.4 on 2023-02-05 00:36

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0007_alter_question_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='options',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=200), size=None),
        ),
    ]