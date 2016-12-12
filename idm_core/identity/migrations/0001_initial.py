# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-12-12 11:14
from __future__ import unicode_literals

import dirtyfields.dirtyfields
from django.db import migrations, models
import django.db.models.deletion
import django_fsm
import idm_core.identity.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Identity',
            fields=[
                ('id', models.UUIDField(default=idm_core.identity.models.get_uuid, editable=False, primary_key=True, serialize=False)),
                ('label', models.CharField(blank=True, max_length=1024)),
                ('qualified_label', models.CharField(blank=True, max_length=1024)),
                ('sort_label', models.CharField(blank=True, max_length=1024)),
                ('state', django_fsm.FSMField(choices=[('established', 'established'), ('active', 'active'), ('archived', 'archived'), ('suspended', 'suspended'), ('merged', 'merged')], default='established', max_length=50)),
                ('primary_email', models.EmailField(blank=True, max_length=254)),
                ('primary_username', models.CharField(blank=True, max_length=32)),
                ('begin_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('extant', models.BooleanField(default=True)),
                ('sex', models.CharField(choices=[('0', 'not known'), ('1', 'male'), ('2', 'female'), ('9', 'not applicable')], default='0', max_length=1)),
                ('role_label', models.CharField(blank=True, max_length=1024)),
                ('claim_code', models.UUIDField(blank=True, null=True)),
                ('merged_into', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='merged_from', to='identity.Identity')),
                ('organization', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='role_identity', to='identity.Identity')),
            ],
            options={
                'verbose_name_plural': 'identities',
                'verbose_name': 'identity',
            },
            bases=(dirtyfields.dirtyfields.DirtyFieldsMixin, models.Model),
        ),
        migrations.CreateModel(
            name='IdentityType',
            fields=[
                ('id', models.CharField(max_length=32, primary_key=True, serialize=False)),
                ('label', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('uuid', models.UUIDField(default=idm_core.identity.models.get_uuid, editable=False, primary_key=True, serialize=False)),
                ('identity', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='identity.Identity')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
