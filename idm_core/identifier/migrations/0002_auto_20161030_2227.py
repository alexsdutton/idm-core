# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-30 22:27
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('identifier', '0001_initial'),
        ('idm_core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='identifier',
            name='identity',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='idm_core.Identity'),
        ),
        migrations.AddField(
            model_name='identifier',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='identifier.IdentifierType'),
        ),
        migrations.AlterUniqueTogether(
            name='identifier',
            unique_together=set([('type', 'value')]),
        ),
        migrations.AlterIndexTogether(
            name='identifier',
            index_together=set([('type', 'value'), ('type', 'identity')]),
        ),
    ]