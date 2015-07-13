# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('browse', '0011_comment_top_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='publication',
            name='description',
            field=models.CharField(blank=True, max_length=1000),
            preserve_default=True,
        ),
    ]
