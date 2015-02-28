# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('browse', '0003_auto_20150222_1424'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='date',
            field=models.DateTimeField(default=datetime.datetime.now, verbose_name='date'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='document',
            name='save_date',
            field=models.DateTimeField(default=datetime.datetime.now, verbose_name='date saved'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='message',
            name='date',
            field=models.DateTimeField(default=datetime.datetime.now, verbose_name='date'),
            preserve_default=True,
        ),
    ]
