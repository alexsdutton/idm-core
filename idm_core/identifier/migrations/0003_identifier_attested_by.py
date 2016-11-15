# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-11-10 20:02
from __future__ import unicode_literals

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('identifier', '0002_auto_20161106_1507'),
    ]

    operations = [
        migrations.AddField(
            model_name='identifier',
            name='attested_by',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(choices=[('driving-license', 'Driving license'), ('passport', 'Passport'), ('national-identity-document', 'National identity document'), ('bill', 'Bill'), ('visa', 'Visa'), ('deed-poll', 'Deed poll'), ('other', 'Other')], max_length=32), default=[], size=None),
        ),
    ]