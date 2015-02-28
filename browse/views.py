from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.core.urlresolvers import reverse
from django.views import generic
from django.utils import timezone
from django import template
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q

import json

from django.contrib.auth.forms import UserCreationForm

register = template.Library()

from django.contrib.auth import authenticate, login, logout, get_user

from browse.models import Document, PublishedDocument, Bookmark, EditRequest, Comment, Vote, Publication, TwoCentsUser, Message, Link, Tag
from django.contrib.auth.models import User

from django.core import serializers

# Create your views here.

def article_preview_context(request, page):
    u = get_user(request)
    tags = u.twocentsuser.active_tags.all()
    if len(tags) > 0:
        latest_document_list = PublishedDocument.objects.filter(pub_date__lte=timezone.now(), tags__in=tags).order_by('-rank')
    else:
        latest_document_list = PublishedDocument.objects.filter(pub_date__lte=timezone.now()).order_by('-rank')

    paginator = Paginator(latest_document_list, 48)
    try:
        returned_docs = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        returned_docs = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        returned_docs = paginator.page(paginator.num_pages)

    #    context = {'latest_document_list': latest_document_list}
    bookmark_list = Bookmark.objects.filter(user=u.id).order_by('-bookmark_date')[:5]
    
    vote_dict = []
    bookmark_dict = []
    for d in returned_docs:
        try:
            vote = Vote.objects.get(user = u, document = d)
            if (vote.active):
                vote_dict.append(d.id)
        except:
            pass
        try:
            bookmark = Bookmark.objects.get(user = u, doc = d)
            if (bookmark.active):
                bookmark_dict.append(d.id)
        except:
            pass
    context = {'bookmark_list': bookmark_list, 'latest_document_list': returned_docs, 'doc_votes': vote_dict, 'bookmarks': bookmark_dict, 'page': page}
    return context

def article_previews(request, page):
    context = article_preview_context(request, page)
    return render(request, 'browse/articles.html', context)

def index(request):
    return browse_page(request, 1)

def browse_page(request, page):
    context = article_preview_context(request, page)
    form = UserCreationForm()
    context['form'] = form
    return render(request, 'browse/index.html', context)


def author(request, name):
    profile_user = User.objects.get(username__iexact=name)
    u = get_user(request)
    latest_document_list = PublishedDocument.objects.filter(pub_date__lte=timezone.now(), user=profile_user).order_by('-pub_date')[:16]
#    context = {'latest_document_list': latest_document_list}
    bookmark_list = Bookmark.objects.filter(user=u.id).order_by('-bookmark_date')[:5]
    
    publication_list = Publication.objects.filter(editors=profile_user)
    
    JSONSerializer = serializers.get_serializer("json")
    json_serializer = JSONSerializer()
    
    vote_dict = []
    bookmark_dict = []
    for d in latest_document_list:
        try:
            vote = Vote.objects.get(user = u, document = d)
            if (vote.active):
                vote_dict.append(d.id)
        except:
            pass
        try:
            bookmark = Bookmark.objects.get(user = u, doc = d)
            if (bookmark.active):
                bookmark_dict.append(d.id)
        except:
            pass
    is_subscribed = False
    if (u.is_authenticated() and u.twocentsuser.user_follows.filter(id=profile_user.id).exists()):
        is_subscribed = True
            
    context = {'bookmark_list': bookmark_list, 'latest_document_list': latest_document_list, 'doc_votes': vote_dict, 'bookmarks': bookmark_dict, 'author' : profile_user, 'publications' : json_serializer.serialize(publication_list, fields="publication_name"), 'subscribed' : is_subscribed}
    return render(request, 'browse/author.html', context)

def save_author_desc(request):
    u = get_user(request)
    desc = request.POST['desc']
    twocentsuser = u.twocentsuser
    twocentsuser.author_description = desc
    twocentsuser.save()
    return HttpResponse(desc)


def publication(request, name):
    pub = Publication.objects.get(publication_name=name)
    u = get_user(request)
    latest_document_list = PublishedDocument.objects.filter(publication=pub).order_by('-pub_date')[:16]
    
    vote_dict = {}
    for d in latest_document_list:
        try:
            vote = Vote.objects.get(user = u, document = d)
            vote_dict[str(d.id)] = vote.active
        except:
            vote_dict[str(d.id)] = False
            
    context = {'latest_document_list': latest_document_list, 'doc_votes': json.dumps(vote_dict)}
    return render(request, 'browse/index.html', context)
    
def read(request, hash_id):
    try:
        doc = Document.objects.get(link_hash=hash_id)
        if doc.has_been_published:
            doc = PublishedDocument.objects.get(original_id=doc.original_id)
    except:
        doc = PublishedDocument.objects.get(link_hash=hash_id)
    context = {'selected_doc': doc, 'bookmark' : get_bookmark_offset(request, doc)}
    return render(request, 'browse/read.html', context)

def get_latest_bookmarks(request):
    count = int(request.POST['count'])
    u = get_user(request)
    bookmark_list = Bookmark.objects.filter(user=u.id).order_by('-bookmark_date')[:count]
    response = ""
    doc_list = []
    for b in bookmark_list:
        if b.active:
            doc_list.append(b.doc)
    XMLSerializer = serializers.get_serializer("xml")
    xml_serializer = XMLSerializer()
    return HttpResponse(xml_serializer.serialize(doc_list, fields="document_title, link_hash"))

def get_latest_docs(request):
    count = int(request.POST['count'])
    u = get_user(request)
    doc_list = Document.objects.filter(user=u.id, is_latest=True, is_edit=False).order_by('-save_date')[:count]
    response = ""
    XMLSerializer = serializers.get_serializer("xml")
    xml_serializer = XMLSerializer()
    pubs = {}
    sub_pubs = {}
    for d in doc_list:
        try:
            pub_doc = PublishedDocument.objects.get(original_id=d.original_id)
            doc_pubs = pub_doc.publication_set.all()
            pubs_xml = xml_serializer.serialize(doc_pubs, fields="publication_name")
        except:
            pubs_xml = ""
        try:
            o = d.original_id
            doc_sub_pubs = o.publication_set.all()
            sub_pubs_xml = xml_serializer.serialize(doc_sub_pubs, fields="publication_name")
        except:
            sub_pubs_xml = ""
        pubs[d.id] = pubs_xml
        sub_pubs[d.id] = sub_pubs_xml
        
    context = {"docs" : xml_serializer.serialize(doc_list, fields="document_title, link_hash, editors_list, original_id.has_been_published"), "pubs" : pubs, "sub_pubs" : sub_pubs}
#    return HttpResponse(xml_serializer.serialize(pubs, fields="publication_name"))
    return HttpResponse(json.dumps(context))

def get_latest_revs(request):
    count = int(request.POST['count'])
    u = get_user(request)
    doc_list = Document.objects.filter(user=u.id, is_latest=True, has_been_published=False).order_by('-save_date')[:count]
    response = ""
    XMLSerializer = serializers.get_serializer("xml")
    xml_serializer = XMLSerializer()
    return HttpResponse(xml_serializer.serialize(doc_list, fields="document_title, link_hash, edit_count, editors_list, original_id.has_been_published"))

def get_latest_edits(request):
    count = int(request.POST['count'])
    u = get_user(request)
    edit_list = EditRequest.objects.filter(editor=u.id).order_by('-request_date')[:count]
    response = ""
    doc_list = []
    for e in edit_list:
        doc_list.append(e.doc)
    XMLSerializer = serializers.get_serializer("xml")
    xml_serializer = XMLSerializer()
    return HttpResponse(xml_serializer.serialize(doc_list, fields="document_title, link_hash"))

def get_comments(request):
    doc_id = request.GET['doc_id']
    doc=PublishedDocument.objects.get(pk=doc_id)
    u = get_user(request)
    comment_list = Comment.objects.filter(document=doc).order_by('-date')[:20]
    XMLSerializer = serializers.get_serializer("xml")
    xml_serializer = XMLSerializer()
    
    vote_dict = {}
    for c in comment_list:
        try:
            vote = Vote.objects.get(user = u, comment = c)
            vote_dict[str(c.id)] = vote.active
        except:
            vote_dict[str(c.id)] = False
    context = {}
    context['comments']= xml_serializer.serialize(comment_list)
    context['comment_votes']= vote_dict
    context['count']= len(comment_list)

    return HttpResponse(json.dumps(context))

def get_subscriptions(request):
    u = get_user(request)
    pub_list = u.twocentsuser.pub_follows.all().order_by('-last_pub_date')
    pubs = []
    for p in pub_list:
        pubs.append(p.publication_name)
    context = {'publications': pubs}
    
    user_list = u.twocentsuser.user_follows.all()
    us = []
    for user in user_list:
        us.append(user.username)
    context = {'users': us}
    return HttpResponse(json.dumps(context))


def add_bookmark(request):
    char_offset = request.POST['offset']
    doc_id = request.POST['doc_id']
    active = request.POST['active']
    if (active == "true"):
        activate = True
    else:
        activate = False
    u = get_user(request)
    b = Bookmark.objects.filter(user=User.objects.get(pk=u.id), doc=PublishedDocument.objects.get(pk=doc_id)).first()
    if b is not None:
        b.bookmark_date=timezone.now()
        b.active = activate
        b.offset = char_offset
    else:
        b = Bookmark(user=User.objects.get(pk=u.id), doc=PublishedDocument.objects.get(pk=doc_id), bookmark_date=timezone.now(), offset = char_offset)
    b.save()
    return get_latest_bookmarks(request)

def get_bookmark_offset(request, document):
    u = get_user(request)
    try:
        b = Bookmark.objects.get(user=u, doc=document)
        if (b.active == True):
            return b.offset
        else:
            return "none"
            
    except:
        return "none"

def update_votes(doc, voter):
    try:
        vote = Vote.objects.get(user=voter, document=doc)
        if (vote.active):
            doc.dec_votes()
            vote.active = False
            vote.save()
        else:
            doc.inc_votes()
            vote.active = True
            vote.save() 
    except Vote.DoesNotExist:
        doc.inc_votes()
        vote = Vote(user=voter, document=doc, active=True)
        vote.save()

def update_comment_votes(comm, voter):
    try:
        vote = Vote.objects.get(user=voter, comment=comm)
        if (vote.active):
            comm.dec_votes()
            vote.active = False
            vote.save()
        else:
            comm.inc_votes()
            vote.active = True
            vote.save() 
    except Vote.DoesNotExist:
        comm.inc_votes()
        vote = Vote(user=voter, comment=comm, active=True)
        vote.save()
    

def add_vote(request):
    doc_id = request.POST['doc_id']
    u = get_user(request)
    doc=PublishedDocument.objects.get(pk=doc_id)
    update_votes(doc, u)
    return HttpResponse(doc.votes)
    

def add_comment_vote(request):
    comment_id = request.POST['comment_id']
    u = get_user(request)
    comment=Comment.objects.get(pk=comment_id)
    update_comment_votes(comment, u)
    return HttpResponse(comment.votes)

def add_comment(request):
    doc_id = request.POST['doc_id']
    u = get_user(request)
    text = request.POST['comment_text']
    doc=PublishedDocument.objects.get(pk=doc_id)
    try:
        reply = request.POST['parent']
        parent_comment = Comment.objects.get(pk=reply)
        comment = Comment(user = u, username = u.username, document = doc, comment_text = text, parent = parent_comment, date=timezone.now())
    except:
        comment = Comment(user = u, username = u.username,  document = doc, comment_text = text, date=timezone.now())
        
    comment.save()
    comment_list = [comment]
    XMLSerializer = serializers.get_serializer("xml")
    xml_serializer = XMLSerializer()
    return HttpResponse(xml_serializer.serialize(comment_list))

def send_message(request):
    recipient_name = request.POST['recipient']
    rec = User.objects.get(username=recipient_name)
    tcu = rec.twocentsuser
    tcu.has_unread_message = True
    tcu.save()

    u = get_user(request)
    text = request.POST['message_content']
    try:
        reply = request.POST['parent']
        parent_comment = Message.objects.get(pk=reply)
        if parent_comment.original_message is None:
            orig_message = parent_comment
        else:
            orig_message = parent_comment.original_message
        message = Message(sender = u, recipient = rec, message_text = text, previous = parent_comment, original_message = orig_message, date=timezone.now())
        message.save()
    except:
        message = Message(sender = u, recipient = rec, message_text = text, date=timezone.now())
        message.save()

        
    return author(request, recipient_name)

def messages(request, page):
    u = get_user(request)
    tcu = u.twocentsuser
    tcu.has_unread_message = False
    tcu.save()
    message_list = Message.objects.filter(recipient = u)

    paginator = Paginator(message_list, 15)
    try:
        returned_messages = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        returned_messages = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        returned_messages = paginator.page(paginator.num_pages)

    context = {'messages': returned_messages}
    return render(request, 'browse/messages.html', context)

def sent_messages(request, page):
    u = get_user(request)
    message_list = Message.objects.filter(sender = u)

    paginator = Paginator(message_list, 15)
    try:
        returned_messages = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        returned_messages = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        returned_messages = paginator.page(paginator.num_pages)

    context = {'messages': returned_messages}
    return render(request, 'browse/sent.html', context)

def conversations(request, page):
    u = get_user(request)
    message_list = Message.objects.filter(Q(recipient = u) | Q(sender = u), original_message = None)

    paginator = Paginator(message_list, 50)
    try:
        original_messages = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        original_messages = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        original_messages = paginator.page(paginator.num_pages)

    full_message_list = Message.objects.filter(original_message__in=original_messages)
        
    context = {'full_messages': full_message_list, 'original_messages': original_messages}
    return render(request, 'browse/conversations.html', context)
        
        
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('browse:index'))
    
@register.inclusion_tag('login.html') 
def login_form(request):
    username = request.POST['username']
    password = request.POST['password1']
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            
            return HttpResponseRedirect(reverse('browse:index'))
            # Redirect to a success page.
        else:
            return HttpResponseRedirect(reverse('browse:index'))
            # Return a 'disabled account' error message
    else:
            return HttpResponseRedirect(reverse('browse:index'))
            # Return an 'invalid login' error message.
            

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            two_cents_user = TwoCentsUser(user = new_user)
            two_cents_user.save()
            return login_form(request)
    else:
        form = UserCreationForm()
    return render(request, "browse/register.html", {
        'form': form,
    })

        
def follow_user(request):
    u = get_user(request).twocentsuser
    member_name = request.POST['username']
    target_author = User.objects.get(username=member_name)
    u.user_follows.add(target_author)
    u.save()
    return HttpResponse(member_name)

        
def follow_pub(request):
    u = get_user(request).twocentsuser
    pub_id = request.POST['publication_id']
    target_pub = Publication.objects.get(pk=pub_id)
    u.pub_follows.add(target_pub)
    u.save()
    return HttpResponse(pub_id)

def new_link(request):
    u = get_user(request)
    target = request.POST['href']
    display = request.POST['display_name']
    if not (target.startswith("http://")):
        target = "http://" + target
    l = Link(user = u, href = target, display_name = display)
    l.save()
    return author(request, u.username)

def follow_tags(request):
    tags = request.POST['tags']
    tag_list = tags.split(":")
    u = get_user(request).twocentsuser
    for tag in tag_list:
        tag_text = tag.lower()
        if tag_text != "":
            try:
                t = Tag.objects.get(text = tag_text)
            except:
                t = Tag(text = tag_text)
                t.save()
            u.tag_follows.add(t)
            u.active_tags.add(t)
    u.save()
    return HttpResponseRedirect(reverse('browse:index'))

def add_tags(request):
    tags = request.POST['tags']
    doc_id = request.POST['doc_id']
    tag_list = tags.split(":")
    doc = PublishedDocument.objects.get(pk = doc_id)
    for tag in tag_list:
        tag_text = tag.lower()
        if tag_text != "":
            try:
                t = Tag.objects.get(text = tag_text)
            except:
                t = Tag(text = tag_text)
                t.save()
            doc.tags.add(t)
    doc.save()
    return HttpResponseRedirect(reverse('browse:index'))
        
def toggle_tag(request):
    tag = request.POST['tag']
    page = request.POST['page']
    tag_text = tag.lower()
    u = get_user(request).twocentsuser
    if tag_text != "":
        try:
            t = Tag.objects.get(text = tag_text)
        except:
            t = Tag(text = tag_text)
            t.save()
            u.tag_follows.add(t)
            u.active_tags.add(t)
            u.save()
            return article_previews(request, page)
        if (not t in u.tag_follows.all()):
            u.tag_follows.add(t)
            u.active_tags.add(t)
        elif (not t in u.active_tags.all()):
            u.active_tags.add(t)
        else:
            u.active_tags.remove(t)
        u.save()
    return article_previews(request, page)
            
            