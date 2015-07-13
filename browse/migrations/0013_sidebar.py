# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('browse', '0012_publication_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='Sidebar',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('title', models.CharField(blank=True, max_length=60)),
                ('content', models.CharField(blank=True, max_length=1000)),
                ('publication', models.ForeignKey(to='browse.Publication')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
