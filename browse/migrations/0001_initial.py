# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Bookmark',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('offset', models.IntegerField(default=0)),
                ('active', models.BooleanField(default=True)),
                ('bookmark_date', models.DateTimeField(verbose_name='date bookmarked')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Citation',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('authors', models.CharField(default='', max_length=300)),
                ('publisher', models.CharField(default='', max_length=300)),
                ('title', models.CharField(default='', max_length=300)),
                ('website', models.CharField(default='', max_length=300)),
                ('version', models.CharField(default='', max_length=300)),
                ('url', models.CharField(default='', max_length=300)),
                ('pages', models.CharField(default='', max_length=300)),
                ('source_type', models.CharField(default='', max_length=100)),
                ('pub_date', models.DateTimeField(verbose_name='pub_date', null=True)),
                ('access_date', models.DateTimeField(verbose_name='access_date', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('username', models.CharField(default='Anonymous', max_length=30)),
                ('date', models.DateTimeField(default=datetime.datetime(2015, 2, 22, 19, 14, 25, 493975, tzinfo=utc), verbose_name='date')),
                ('comment_text', models.CharField(max_length=1000)),
                ('votes', models.IntegerField(default=1)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('document_text', models.CharField(max_length=10000, blank=True)),
                ('document_title', models.CharField(max_length=200)),
                ('document_version', models.IntegerField(default=0)),
                ('is_edit', models.BooleanField(default=False)),
                ('is_latest', models.BooleanField(default=False)),
                ('is_published', models.BooleanField(default=False)),
                ('edit_count', models.IntegerField(default=0)),
                ('editors_list', models.CharField(default='', max_length=200)),
                ('save_date', models.DateTimeField(default=datetime.datetime(2015, 2, 22, 19, 14, 25, 493975, tzinfo=utc), verbose_name='date saved')),
                ('pub_date', models.DateTimeField(verbose_name='date published', null=True)),
                ('link_hash', models.CharField(default='', max_length=20, editable=False)),
                ('has_been_published', models.BooleanField(default=False)),
                ('has_comments', models.BooleanField(default=False)),
                ('editor', models.ForeignKey(related_name='document_editor', default=0, to=settings.AUTH_USER_MODEL)),
                ('latest_id', models.ForeignKey(default=0, to='browse.Document')),
                ('original_id', models.ForeignKey(related_name='orig_id', default=0, to='browse.Document')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EditRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('comment', models.CharField(default='', max_length=1000)),
                ('request_date', models.DateTimeField(verbose_name='date requested')),
                ('doc', models.ForeignKey(to='browse.Document')),
                ('editor', models.ForeignKey(related_name='editrequest_editor', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Link',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('href', models.CharField(max_length=200)),
                ('display_name', models.CharField(max_length=100)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('date', models.DateTimeField(default=datetime.datetime(2015, 2, 22, 19, 14, 25, 493975, tzinfo=utc), verbose_name='date')),
                ('message_text', models.CharField(max_length=1000)),
                ('original_message', models.ForeignKey(related_name='original', null=True, to='browse.Message')),
                ('previous', models.ForeignKey(default=0, to='browse.Message')),
                ('recipient', models.ForeignKey(related_name='recipient', to=settings.AUTH_USER_MODEL)),
                ('sender', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Notecard',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('notecard_text', models.CharField(max_length=10000)),
                ('tag_string', models.CharField(max_length=1000)),
                ('document', models.ForeignKey(to='browse.Document')),
                ('source', models.ForeignKey(to='browse.Citation')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Publication',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('accepts_articles', models.BooleanField(default=False)),
                ('publication_name', models.CharField(default='default', max_length=200)),
                ('last_pub_date', models.DateTimeField(verbose_name='pub_date', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PublishedDocument',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('document_text', models.CharField(max_length=10000, blank=True)),
                ('preview_text', models.CharField(max_length=1000, blank=True)),
                ('document_title', models.CharField(max_length=200)),
                ('has_comments', models.BooleanField(default=True)),
                ('pub_date', models.DateTimeField(verbose_name='date published', null=True)),
                ('link_hash', models.CharField(default='', max_length=20, editable=False)),
                ('votes', models.IntegerField(default=1)),
                ('rank', models.FloatField(default=0)),
                ('original_id', models.ForeignKey(related_name='orig_doc_id', default=0, to='browse.Document')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TwoCentsUser',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('author_description', models.CharField(max_length=1000, blank=True)),
                ('last_pub_date', models.DateTimeField(verbose_name='pub_date', null=True)),
                ('has_unread_message', models.BooleanField(default=False)),
                ('pub_follows', models.ManyToManyField(related_name='pub_follows', to='browse.Publication')),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
                ('user_follows', models.ManyToManyField(related_name='user_follows', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('active', models.BooleanField(default=False)),
                ('comment', models.ForeignKey(null=True, to='browse.Comment')),
                ('document', models.ForeignKey(null=True, to='browse.PublishedDocument')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='publication',
            name='articles',
            field=models.ManyToManyField(to='browse.PublishedDocument'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='publication',
            name='editors',
            field=models.ManyToManyField(related_name='publication_editors', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='publication',
            name='owner',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='publication',
            name='pendingArticles',
            field=models.ManyToManyField(to='browse.Document'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='publication',
            name='writers',
            field=models.ManyToManyField(related_name='publication_writers', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='editrequest',
            name='publication',
            field=models.ForeignKey(null=True, to='browse.Publication'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='editrequest',
            name='writer',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='comment',
            name='document',
            field=models.ForeignKey(to='browse.PublishedDocument'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='comment',
            name='parent',
            field=models.ForeignKey(default=0, to='browse.Comment'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='comment',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='citation',
            name='document',
            field=models.ForeignKey(to='browse.Document'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='citation',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='bookmark',
            name='doc',
            field=models.ForeignKey(to='browse.PublishedDocument'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='bookmark',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
