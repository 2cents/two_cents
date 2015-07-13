# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('browse', '0008_auto_20150322_1500'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='save_date',
            field=models.DateTimeField(default=datetime.datetime.now, verbose_name='date saved'),
            preserve_default=True,
        ),
    ]
