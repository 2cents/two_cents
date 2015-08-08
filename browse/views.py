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
from django.db.models import Q

from browse.models import Document, PublishedDocument, Bookmark, EditRequest, Comment, Vote, Publication, TwoCentsUser, Message, Link, Tag, DocumentDraft, RecentlyRead
from django.contrib.auth.models import User

from django.core import serializers

# Create your views here.

def sphere(request):
    return render(request, 'browse/sphere.html')

def get_recently_read(user):
    recent_articles = RecentlyRead.objects.filter(user = user).order_by('-date')
    return recent_articles

def add_recently_read(user, doc):
    recent_articles = get_recently_read(user)
    if recent_articles.filter(article = doc).exists():
        earliest_article = recent_articles.get(article = doc)
        earliest_article.save()
        return recent_articles[1:]
    elif len(recent_articles) > 5:
        earliest_article = recent_articles[5]
        earliest_article.article = doc
        earliest_article.save()
    else:
        earliest_article = RecentlyRead(user = user, article = doc)
        earliest_article.save()
    return recent_articles[:5]

def auth_redirect(user, request):
    if not user.is_authenticated():
        return browse_page(request, 1)
    else:
        pass

def article_preview_context(request, page):
    u = get_user(request)
    recent_articles = []
    if (u.is_authenticated()):
        recent_articles = get_recently_read(u)[:5]
        tags = u.twocentsuser.active_tags.all()
        if len(tags) > 0:
            latest_document_list = PublishedDocument.objects.filter(Q(publication__in=u.twocentsuser.pub_follows.all()) | Q(user__in=u.twocentsuser.user_follows.all(), unlisted = False) | Q(pub_date__lte=timezone.now(), tags__in=tags, unlisted = False)).distinct().order_by('-rank')
        else:
            latest_document_list = PublishedDocument.objects.filter(Q(publication__in=u.twocentsuser.pub_follows.all(), unlisted = False) | Q(pub_date__lte=timezone.now(), unlisted = False) | Q(user__in=u.twocentsuser.user_follows.all())).distinct().order_by('-rank')
    else:
        tags = []
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
    context = {'bookmark_list': bookmark_list, 'latest_document_list': returned_docs, 'doc_votes': vote_dict, 'bookmarks': bookmark_dict, 'page': page, 'recent_articles' : recent_articles}
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
    form = UserCreationForm()
    context['form'] = form
    return render(request, 'browse/author.html', context)

def save_author_desc(request):
    u = get_user(request)
    desc = request.POST['desc']
    twocentsuser = u.twocentsuser
    twocentsuser.author_description = desc
    twocentsuser.save()
    return HttpResponse(desc)

def save_pub_desc(request):
    u = get_user(request)
    desc = request.POST['desc']
    pub_id = request.POST['publication_id']
    pub = Publication.objects.get(pk = pub_id)
    pub.description = desc
    pub.save()
    return HttpResponse(desc)


def publication(request, name):
    pub = Publication.objects.get(publication_name__iexact=name)
    u = get_user(request)
    if pub.is_open:
        latest_document_list = PublishedDocument.objects.filter(publication=pub).order_by('-rank')[:16]        
    else:
        latest_document_list = PublishedDocument.objects.filter(publication=pub).order_by('-pub_date')[:16]
    
    is_subscribed = False
    if (u.is_authenticated() and u.twocentsuser.pub_follows.filter(id=pub.id).exists()):
        is_subscribed = True
    
    vote_dict = {}
    for d in latest_document_list:
        try:
            vote = Vote.objects.get(user = u, document = d)
            vote_dict[str(d.id)] = vote.active
        except:
            vote_dict[str(d.id)] = False
            
    context = {'latest_document_list': latest_document_list, 'doc_votes': json.dumps(vote_dict), 'publication':pub, 'subscribed' : is_subscribed}
    form = UserCreationForm()
    context['form'] = form
    return render(request, 'browse/publication.html', context)
    
    
def read(request, hash_id):
    u = get_user(request)
    recent_articles = []
    try:
        orig_doc = Document.objects.get(link_hash=hash_id)
        if orig_doc.has_been_published:
            doc = PublishedDocument.objects.get(original_id=orig_doc)
            if u.is_authenticated():
                recent_articles = add_recently_read(u, doc)
        else:
            doc = doc.latest_id
    except:
        doc = PublishedDocument.objects.get(link_hash=hash_id)
        if u.is_authenticated():
            recent_articles = add_recently_read(u, doc)
    context = {'selected_doc': doc, 'bookmark' : get_bookmark_offset(request, doc), 'recent_articles' : recent_articles}
    form = UserCreationForm()
    context['form'] = form
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

def get_latest_pub_submissions(request):
    count = int(request.POST['count'])
    u = get_user(request)
    pub_list = Publication.objects.filter(editors=u.id)[:count]
    pubs = []
    for pub in pub_list:
        pub_stats = [pub.publication_name, pub.pendingArticles.all().exists()]
        pubs.append(pub_stats)
        
    XMLSerializer = serializers.get_serializer("xml")
    xml_serializer = XMLSerializer()
    context = {"docs" : pubs}
#    return HttpResponse(xml_serializer.serialize(pubs, fields="publication_name"))
    return HttpResponse(json.dumps(context))
    

def get_latest_docs(request):
    count = int(request.POST['count'])
    u = get_user(request)
    doc_list = Document.objects.filter(user=u.id).order_by('-save_date')[:count]
    response = ""
    JSONSerializer = serializers.get_serializer("json")
    json_serializer = JSONSerializer()
    pubs = {}
    sub_pubs = {}
    editors = {}
    docs = []
    unlisted = False
    for d in doc_list:
        pubs_json = []
        sub_pubs_json = []
        try:
            pub_doc = PublishedDocument.objects.get(original_id=d)
            unlisted = pub_doc.unlisted
            doc_pubs = pub_doc.publication_set.all()
            for pub in doc_pubs:
                pubs_json.append(pub.publication_name)
#            pubs_xml = json_serializer.serialize(doc_pubs, fields="publication_name")
        except:
            pubs_json = []
            pubs_xml = ""
        try:
            doc_sub_pubs = d.publication_set.all()
            for pub in doc_sub_pubs:
                sub_pubs_json.append(pub.publication_name)
 #           sub_pubs_xml = json_serializer.serialize(doc_sub_pubs, fields="publication_name")
        except:
            sub_pubs_json = []
            sub_pubs_xml = ""
        try:
            editors[d.document_title] = d.latest_id.editors_list
        except:
            editors[d.document_title] = ""
        pubs[d.id] = pubs_json
        sub_pubs[d.id] = sub_pubs_json
        docs.append({"document_title": d.document_title, "link_hash": d.link_hash, "editors_list": d.editors_list, "has_been_published":d.has_been_published, "unlisted": unlisted, "pk": d.id})
    
    context = {"docs" : docs, "pubs" : pubs, "sub_pubs" : sub_pubs, "editors" : editors}
#    return HttpResponse(xml_serializer.serialize(pubs, fields="publication_name"))
    return HttpResponse(json.dumps(context))

def get_latest_revs(request):
    count = int(request.POST['count'])
    u = get_user(request)
    doc_list = Document.objects.filter(user=u.id, has_been_published=False).order_by('-save_date')[:count]
    response = ""
    XMLSerializer = serializers.get_serializer("xml")
    xml_serializer = XMLSerializer()
    return HttpResponse(xml_serializer.serialize(doc_list, fields="document_title, link_hash, latest_id.edit_count, latest_id.editors_list, original_id.has_been_published"))

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


def get_replies(request, comment_id):
#    comment_id = request.GET['comment_id']
#    full_replies = request.GET['full_replies']
    full_replies = 'false'
    top = Comment.objects.get(pk = comment_id)
    u = get_user(request)
    full_comments = Comment.objects.filter(top_comment=top).exclude(pk=top.id).order_by('-date')
    if (full_replies=='true'):
        comment_list = full_comments[2:]
    else:
        comment_list = full_comments[:2]
    XMLSerializer = serializers.get_serializer("xml")
    xml_serializer = XMLSerializer()
    
    vote_dict = {}
    replies_dict = {}
    for c in comment_list:
        try:
            vote = Vote.objects.get(user = u, comment = c)
            vote_dict[str(c.id)] = vote.active
        except:
            vote_dict[str(c.id)] = False
    context = {}
    context['comments']= xml_serializer.serialize(comment_list)
    context['comment_votes']= vote_dict
    context['count']= len(full_comments)
    context['replies'] = replies_dict

    return json.dumps(context)



def get_full_replies(request):
    comment_id = request.GET['comment_id']
    top = Comment.objects.get(pk = comment_id)
    comment_list = Comment.objects.filter(top_comment=top).order_by('-date')
    XMLSerializer = serializers.get_serializer("xml")
    xml_serializer = XMLSerializer()
    u = get_user(request)
    
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

def get_comments(request):
    doc_id = request.GET['doc_id']
    doc=PublishedDocument.objects.get(pk=doc_id)
    u = get_user(request)
    comment_list = Comment.objects.filter(document=doc, parent=None).order_by('-date')[:20]
    XMLSerializer = serializers.get_serializer("xml")
    xml_serializer = XMLSerializer()
    
    vote_dict = {}
    replies_dict = {}
    for c in comment_list:
        replies_dict[c.id] = get_replies(request, c.id)
        try:
            vote = Vote.objects.get(user = u, comment = c)
            vote_dict[str(c.id)] = vote.active
        except:
            vote_dict[str(c.id)] = False
    context = {}
    context['comments']= xml_serializer.serialize(comment_list)
    context['comment_votes']= vote_dict
    context['count']= len(comment_list)
    context['replies'] = replies_dict

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
        top = parent_comment.top_comment
        comment = Comment(user = u, username = u.username, document = doc, comment_text = text, parent = parent_comment, date=timezone.now(), top_comment = top)
    except:
        comment = Comment(user = u, username = u.username,  document = doc, comment_text = text, date=timezone.now())
        comment.save()
        comment.top_comment = comment
        
    comment.save()
    comment_list = [comment]
    XMLSerializer = serializers.get_serializer("xml")
    xml_serializer = XMLSerializer()
    return HttpResponse(xml_serializer.serialize(comment_list))

def send_message_with_args(request, recipient_name, text, u):
    rec = User.objects.get(username=recipient_name)
    tcu = rec.twocentsuser
    tcu.has_unread_message = True
    tcu.save()

    message = Message(sender = u, recipient = rec, message_text = text, date=timezone.now())
    message.save()

        
    return author(request, recipient_name)

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
    last_page = False

    paginator = Paginator(message_list, 15)
    try:
        returned_messages = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        returned_messages = paginator.page(1)
        page = 1
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        returned_messages = paginator.page(paginator.num_pages)
        page = paginator.num_pages
        last_page = True

    context = {'messages': reversed(returned_messages), 'page' : int(page), 'last_page': last_page}
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
    return index(request)
    
@register.inclusion_tag('login.html') 
def login_form(request):
    username = request.POST['username']
    password = request.POST['password1']
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            
            return index(request)
            # Redirect to a success page.
        else:
            return index(request)
            # Return a 'disabled account' error message
    else:
            return index(request)
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
    if u.user_follows.filter(pk = target_author.id).exists():
        u.user_follows.remove(target_author)
    else:
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
    return index(request)

def change_subs(request):
    new_subs = request.POST['new_subs']
    remove_subs = request.POST['remove']
    remove_user_subs = request.POST['remove_user']
    new_subs_list = new_subs.split(":")
    remove_subs_list = remove_subs.split(":")
    remove_user_subs_list = remove_user_subs.split(":")
    u = get_user(request).twocentsuser
    for sub in new_subs_list:
        if sub != "":
            try:
                p = Publication.objects.get(publication_name = sub)
                u.pub_follows.add(p)
            except:
                try:
                    author = User.objects.get(username = sub)
                    u.user_follows.add(author)
                except:
                    pass
    for sub in remove_subs_list:
        if sub != "":
            try:
                p = Publication.objects.get(publication_name = sub)
                u.pub_follows.remove(p)
            except:
                pass
    for sub in remove_user_subs_list:
        if sub != "":
            try:
                author = User.objects.get(username = sub)
                u.user_follows.remove(author)
            except:
                pass
    u.save()
    return index(request)

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
    return index(request)
        
def toggle_tag(request):
    tag = request.POST['tag']
    page = request.POST['page']
    remove = request.POST['remove']
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
        if (not t in u.tag_follows.all() and remove == "false"):
            u.tag_follows.add(t)
            u.active_tags.add(t)
        elif (not t in u.active_tags.all() and remove == "false"):
            u.active_tags.add(t)
        elif (remove == "false"):
            u.active_tags.remove(t)
        elif (remove == "true"):
            u.tag_follows.remove(t)
            u.active_tags.remove(t)
        u.save()
    return article_previews(request, page)
            
            