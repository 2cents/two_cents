# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('browse', '0013_sidebar'),
    ]

    operations = [
        migrations.CreateModel(
            name='PublicationDate',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('date', models.DateTimeField(default=datetime.datetime.now)),
                ('article', models.ForeignKey(to='browse.PublishedDocument')),
                ('publication', models.ForeignKey(to='browse.Publication')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SubmissionDate',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('date', models.DateTimeField(default=datetime.datetime.now)),
                ('article', models.ForeignKey(to='browse.Document')),
                ('publication', models.ForeignKey(to='browse.Publication')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
