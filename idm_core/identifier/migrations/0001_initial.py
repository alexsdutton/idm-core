# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-06-11 21:15
from __future__ import unicode_literals

import dirtyfields.dirtyfields
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Identifier',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attested_by', django.contrib.postgres.fields.ArrayField(base_field=models.SlugField(), blank=True, default=[], size=None)),
                ('identity_id', models.UUIDField()),
                ('value', models.CharField(max_length=64)),
                ('identity_content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
            ],
            bases=(dirtyfields.dirtyfields.DirtyFieldsMixin, models.Model),
        ),
        migrations.CreateModel(
            name='IdentifierType',
            fields=[
                ('id', models.CharField(max_length=32, primary_key=True, serialize=False)),
                ('label', models.CharField(max_length=64)),
                ('applicable_to_all', models.BooleanField(default=False)),
                ('applicable_to', models.ManyToManyField(to='contenttypes.ContentType')),
            ],
            options={
                'ordering': ('id',),
            },
        ),
        migrations.AddField(
            model_name='identifier',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='identifier.IdentifierType'),
        ),
        migrations.AlterUniqueTogether(
            name='identifier',
            unique_together={('type', 'value')},
        ),
        migrations.AlterIndexTogether(
            name='identifier',
            index_together={('type', 'identity_content_type', 'identity_id'), ('type', 'value')},
        ),
    ]
