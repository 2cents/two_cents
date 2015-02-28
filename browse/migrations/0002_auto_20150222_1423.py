# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('browse', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2015, 2, 22, 19, 23, 56, 947572, tzinfo=utc), verbose_name='date'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='document',
            name='save_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 2, 22, 19, 23, 56, 931947, tzinfo=utc), verbose_name='date saved'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='message',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2015, 2, 22, 19, 23, 56, 947572, tzinfo=utc), verbose_name='date'),
            preserve_default=True,
        ),
    ]
