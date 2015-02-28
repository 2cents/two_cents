# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('browse', '0005_auto_20150223_0007'),
    ]

    operations = [
        migrations.AddField(
            model_name='publisheddocument',
            name='tags',
            field=models.ManyToManyField(related_name='tags', to='browse.Tag'),
            preserve_default=True,
        ),
    ]
