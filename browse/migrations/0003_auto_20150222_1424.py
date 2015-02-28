# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('browse', '0002_auto_20150222_1423'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2015, 2, 22, 19, 24, 3, 497034, tzinfo=utc), verbose_name='date'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='document',
            name='save_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 2, 22, 19, 24, 3, 497034, tzinfo=utc), verbose_name='date saved'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='message',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2015, 2, 22, 19, 24, 3, 512658, tzinfo=utc), verbose_name='date'),
            preserve_default=True,
        ),
    ]
