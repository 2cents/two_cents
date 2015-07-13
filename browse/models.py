from datetime import datetime
import hashlib
import math

from hashlib import sha1

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Document(models.Model):
#    document_text = models.CharField(max_length=10000, blank=True, default = None)
    document_title = models.CharField(max_length=200)
#    document_version = models.IntegerField(default=0)
#    original_id = models.ForeignKey('self', related_name="orig_id", default=0)
    latest_id = models.ForeignKey('DocumentDraft', related_name="latest_id", default=0)
    user = models.ForeignKey(User)
#    editor = models.ForeignKey(User, related_name="document_editor", default=0)
#    is_edit = models.BooleanField(default = False)
#    is_latest = models.BooleanField(default = False)
    is_published = models.BooleanField(default = False)
#    edit_count = models.IntegerField(default=0)
    editors_list = models.CharField(max_length=200, default="")
    save_date = models.DateTimeField('date saved', default=datetime.now)
    pub_date = models.DateTimeField('date published', null=True)
    link_hash = models.CharField(max_length=20, editable=False, default="")
    has_been_published = models.BooleanField(default = False)
    has_comments = models.BooleanField(default = False)

    def save(self, *args, **kwargs):
        if self.link_hash=="":
            hashstr = self.document_title + str(self.save_date)
            hashstr_utf = hashstr.encode('utf-8')
            self.link_hash = sha1(hashstr_utf).hexdigest()
        super(Document, self).save(*args, **kwargs)
            
    
    def __str__(self):              # __unicode__ on Python 2
        return self.document_title
    
    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now
    
    def get_original_id(self):
        if self.original_id is not None:
            return self.original_id
        else:
            return self.id
        
    was_published_recently.admin_order_field = 'pub_date'
    was_published_recently.boolean = True
    was_published_recently.short_description = 'Published recently?'
    
class DocumentDraft(models.Model):
    document_text = models.CharField(max_length=10000, blank=True, default = None)
    document_version = models.IntegerField(default=0)
    document = models.ForeignKey(Document)
    editor = models.ForeignKey(User, related_name="document_editor", default=0)
    is_edit = models.BooleanField(default = False)
    is_latest = models.BooleanField(default = False)
    edit_count = models.IntegerField(default=0)
    editors_list = models.CharField(max_length=200, default="")
    save_date = models.DateTimeField('date saved', default=datetime.now)

class Tag(models.Model):
    text = models.CharField(max_length=30, blank=False)

class PublishedDocument(models.Model):
    epoch = datetime(1970, 1, 1)
    
    document_text = models.CharField(max_length=10000, blank=True)
    preview_text = models.CharField(max_length=1000, blank=True)
    document_title = models.CharField(max_length=200)
    original_id = models.ForeignKey(Document, related_name="orig_doc_id", default=0)
    has_comments = models.BooleanField(default = True)
    user = models.ForeignKey(User)
    tags = models.ManyToManyField(Tag, related_name="tags")
    pub_date = models.DateTimeField('date published', null=True)
    link_hash = models.CharField(max_length=20, editable=False, default="")
    votes = models.IntegerField(default=1)
    rank = models.FloatField(default=0)

    def save(self, *args, **kwargs):
        self.preview_text = self.document_text[:1000]
        hashstr = self.document_text + self.document_title + str(self.pub_date)
        hashstr_utf = hashstr.encode('utf-8')
        self.link_hash = sha1(hashstr_utf).hexdigest()
        self.calc_rank()
        super(PublishedDocument, self).save(*args, **kwargs)
    
    def calc_rank(self):
        td = self.pub_date.replace(tzinfo=None) - self.epoch.replace(tzinfo=None)
        td_sec = td.days * 86400 + td.seconds + (float(td.microseconds) / 1000000)
        t = td_sec - 1134028003
        order = math.log(max(self.votes, 1), 10)
        self.rank =  round(order + td_sec / 45000, 7)
        
    def inc_votes(self):
        self.votes = self.votes + 1
        self.save()

        
    def dec_votes(self):
        self.votes = self.votes - 1
        if (self.votes < 1):
            self.votes = 1
        self.save()
        
    
    def __str__(self):              # __unicode__ on Python 2
        return self.document_title
    
    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now
    
    def get_original_id(self):
        if self.original_id is not None:
            return self.original_id
        else:
            return self.id
        
    was_published_recently.admin_order_field = 'pub_date'
    was_published_recently.boolean = True
    was_published_recently.short_description = 'Published recently?'
    
    
class Bookmark(models.Model):
    user = models.ForeignKey(User)
    doc = models.ForeignKey(PublishedDocument)
    offset = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    bookmark_date = models.DateTimeField('date bookmarked')
    
class Publication(models.Model):
    owner = models.ForeignKey(User)
    editors = models.ManyToManyField(User, related_name="publication_editors")
    writers = models.ManyToManyField(User, related_name="publication_writers")
    articles = models.ManyToManyField(PublishedDocument)
    pendingArticles = models.ManyToManyField(Document)
    accepts_articles = models.BooleanField(default = False)
    is_open = models.BooleanField(default = False)
    description = models.CharField(max_length=1000, blank=True)
    publication_name = models.CharField(max_length=200, default="default")
    last_pub_date = models.DateTimeField('pub_date', null=True)

class PublicationDate(models.Model):
    article = models.ForeignKey(PublishedDocument)
    publication = models.ForeignKey(Publication)
    date = models.DateTimeField(default=datetime.now)

class SubmissionDate(models.Model):
    article = models.ForeignKey(Document)
    publication = models.ForeignKey(Publication)
    date = models.DateTimeField(default=datetime.now)

class Sidebar(models.Model):
    publication = models.ForeignKey(Publication)
    title = models.CharField(max_length=60, blank=True)
    content = models.CharField(max_length=1000, blank=True)

class EditRequest(models.Model):
    writer = models.ForeignKey(User)
    editor = models.ForeignKey(User, related_name="editrequest_editor")
    publication = models.ForeignKey(Publication, null=True)
    comment = models.CharField(max_length=1000, default="")
    doc = models.ForeignKey(Document)
    request_date = models.DateTimeField('date requested')
    
class Citation(models.Model):
    user = models.ForeignKey(User)
    authors = models.CharField(max_length=300, default="")
    publisher = models.CharField(max_length=300, default="")
    title = models.CharField(max_length=300, default="")
    website = models.CharField(max_length=300, default="")
    version = models.CharField(max_length=300, default="")
    url = models.CharField(max_length=300, default="")
    pages = models.CharField(max_length=300, default="")
    source_type = models.CharField(max_length=100, default="")
    pub_date = models.DateTimeField('pub_date', null=True)
    access_date = models.DateTimeField('access_date', null=True)
    document = models.ForeignKey(Document)
    
class Comment(models.Model):
    user = models.ForeignKey(User)
    username = models.CharField(max_length=30, default="Anonymous")
    document = models.ForeignKey(PublishedDocument)
    date = models.DateTimeField('date', default=datetime.now)
    comment_text = models.CharField(max_length=1000, blank=False)
    parent = models.ForeignKey('self', default=0)
    top_comment = models.ForeignKey('self', related_name="topmost_comment", default=0)
    votes = models.IntegerField(default=1)
        
    def inc_votes(self):
        self.votes = self.votes + 1
        self.save()

        
    def dec_votes(self):
        self.votes = self.votes - 1
        if (self.votes < 1):
            self.votes = 1
        self.save()
    
    
class Vote(models.Model):
    user = models.ForeignKey(User)
    document = models.ForeignKey(PublishedDocument, null=True)
    comment = models.ForeignKey(Comment, null=True)
    active = models.BooleanField(default=False)
    
class Notecard(models.Model):
    user = models.ForeignKey(User)
    document = models.ForeignKey(Document)
    source = models.ForeignKey(Citation)
    notecard_text = models.CharField(max_length=10000)
    tag_string = models.CharField(max_length=1000)

class TwoCentsUser(models.Model):
    user = models.OneToOneField(User)
    user_follows = models.ManyToManyField(User, related_name="user_follows")
    pub_follows = models.ManyToManyField(Publication, related_name="pub_follows")
    tag_follows = models.ManyToManyField(Tag, related_name="tag_follows")
    active_tags = models.ManyToManyField(Tag, related_name="active_tags")
    author_description = models.CharField(max_length=1000, blank=True)
    last_pub_date = models.DateTimeField('pub_date', null=True)
    has_unread_message = models.BooleanField(default=False)
    def __str__(self):              # __unicode__ on Python 2
        return self.user.username
    
class Link(models.Model):
    href = models.CharField(max_length=200)
    display_name = models.CharField(max_length=100)
    user = models.ForeignKey(User)
    
class Message(models.Model):
    sender = models.ForeignKey(User)
    recipient = models.ForeignKey(User, related_name="recipient")
    date = models.DateTimeField('date', default=datetime.now)
    message_text = models.CharField(max_length=1000, blank=False)
    previous = models.ForeignKey('self', default=0)
    original_message = models.ForeignKey('self', related_name="original", null=True)