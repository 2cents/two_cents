# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('browse', '0007_twocentsuser_active_tags'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentDraft',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('document_text', models.CharField(max_length=10000, blank=True, default=None)),
                ('document_version', models.IntegerField(default=0)),
                ('is_edit', models.BooleanField(default=False)),
                ('is_latest', models.BooleanField(default=False)),
                ('edit_count', models.IntegerField(default=0)),
                ('editors_list', models.CharField(max_length=200, default='')),
                ('save_date', models.DateTimeField(default=datetime.datetime.now, verbose_name='date saved')),
                ('document', models.ForeignKey(to='browse.Document')),
                ('editor', models.ForeignKey(default=0, to=settings.AUTH_USER_MODEL, related_name='document_editor')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='document',
            name='document_text',
        ),
        migrations.RemoveField(
            model_name='document',
            name='document_version',
        ),
        migrations.RemoveField(
            model_name='document',
            name='edit_count',
        ),
        migrations.RemoveField(
            model_name='document',
            name='editor',
        ),
        migrations.RemoveField(
            model_name='document',
            name='is_edit',
        ),
        migrations.RemoveField(
            model_name='document',
            name='is_latest',
        ),
        migrations.RemoveField(
            model_name='document',
            name='original_id',
        ),
        migrations.RemoveField(
            model_name='document',
            name='save_date',
        ),
        migrations.AlterField(
            model_name='document',
            name='latest_id',
            field=models.ForeignKey(default=0, to='browse.DocumentDraft', related_name='latest_id'),
            preserve_default=True,
        ),
    ]
