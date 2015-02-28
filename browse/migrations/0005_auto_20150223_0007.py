# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('browse', '0004_auto_20150222_1425'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('text', models.CharField(max_length=30)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='twocentsuser',
            name='tag_follows',
            field=models.ManyToManyField(related_name='tag_follows', to='browse.Tag'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='document',
            name='document_text',
            field=models.CharField(max_length=10000, blank=True, default=None),
            preserve_default=True,
        ),
    ]
