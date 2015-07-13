# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('browse', '0009_document_save_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='publication',
            name='is_open',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
