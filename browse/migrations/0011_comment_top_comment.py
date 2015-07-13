# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('browse', '0010_publication_is_open'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='top_comment',
            field=models.ForeignKey(related_name='topmost_comment', default=0, to='browse.Comment'),
            preserve_default=True,
        ),
    ]
