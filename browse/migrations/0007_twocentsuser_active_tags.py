# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('browse', '0006_publisheddocument_tags'),
    ]

    operations = [
        migrations.AddField(
            model_name='twocentsuser',
            name='active_tags',
            field=models.ManyToManyField(related_name='active_tags', to='browse.Tag'),
            preserve_default=True,
        ),
    ]
