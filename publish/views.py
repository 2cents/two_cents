from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.core.urlresolvers import reverse
from django.views import generic
from django.utils import timezone
from django import template
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

import json

register = template.Library()

from django.contrib.auth import authenticate, login, logout, get_user

from browse.models import Document, PublishedDocument, EditRequest, Publication, Sidebar, SubmissionDate, PublicationDate
from browse import views
from django.contrib.auth.models import User
# Create your views here.




def review(request, hash_id):
    u = get_user(request)
    views.auth_redirect(u)
    doc = Document.objects.filter(link_hash=hash_id)[0]
#    orig_doc = doc.original_id
#    current_doc = Document.objects.filter(original_id=orig_doc, is_latest=True)[0]
    context = {'selected_doc': doc}
    return render(request, 'publish/review.html', context)

def mydocs(request):
    u = get_user(request)
    views.auth_redirect(u)
    publication_list = Publication.objects.filter(editors=u)
    write_member_list = Publication.objects.filter(writers=u)
    context = {'publication_list': publication_list, 'write_member_list': write_member_list}
    return render(request, 'publish/mydocs.html', context)

def publish_document(request):
    submission_type = request.POST['submissionType']
    hash_id = request.POST['docHash']
    if submission_type == "Publish" or submission_type == "Unlist":
        return(publish_document_to_publication(request))
    
    orig_doc = Document.objects.filter(link_hash=hash_id)[0]
    if submission_type == "Submit to Publication":
        pub_name = request.POST['submit_publication_name']
        pub = Publication.objects.get(publication_name=pub_name)
        if (pub.is_open):
            orig_doc.has_been_published = True;
            orig_doc.save()
            current_doc = orig_doc.latest_id
#            current_doc = Document.objects.filter(original_id=orig_doc, is_latest=True, is_edit=False)[0]
#            Document.objects.filter(original_id=orig_doc).update(has_been_published=True)
            doc_text = current_doc.document_text
            doc_title = orig_doc.document_title
            u = orig_doc.user
            d = PublishedDocument(original_id=orig_doc, user=u, document_text=doc_text, document_title=doc_title, pub_date=timezone.now())
            d.save()
            pub.articles.add(d)
            pub.last_pub_date = d.pub_date
            pub.save()
            tcu = u.twocentsuser
            tcu.last_pub_date = d.pub_date
            tcu.save()
#        orig_doc = doc.original_id
        else:
            if (pub.pendingArticles.filter(pk = orig_doc.id).exists() != True):
                sub_date = SubmissionDate(publication = pub, article = orig_doc)
                sub_date.save()
                pub.pendingArticles.add(orig_doc)
        pub.save()
    else:
 #       orig_doc = doc.original_id
        try:
            current_pub = PublishedDocument.objects.get(original_id = orig_doc)
        except:
            orig_doc.has_been_published = True;
            orig_doc.save()
            current_doc = orig_doc.latest_id
#            current_doc = Document.objects.filter(original_id=orig_doc, is_latest=True, is_edit=False)[0]
#            Document.objects.filter(original_id=orig_doc).update(has_been_published=True)
            doc_text = current_doc.document_text
            doc_title = orig_doc.document_title
            u = orig_doc.user
            d = PublishedDocument(original_id=orig_doc, user=u, document_text=doc_text, document_title=doc_title, pub_date=timezone.now())
            d.save()
            tcu = u.twocentsuser
            tcu.last_pub_date = d.pub_date
            tcu.save()

    return HttpResponseRedirect(reverse('browse:index'))

def publish_document_to_publication(request):
    hash_id = request.POST['docHash']
    pub_name = request.POST['publication_name']
    submission_type = request.POST['submissionType']
    pub = Publication.objects.get(publication_name=pub_name)
    pub_user = get_user(request)
#    orig_doc = doc.original_id
    comment = request.POST.get('comment', "")

    if (submission_type == "Publish"):
        try:
            orig_doc = Document.objects.get(link_hash=hash_id)
            d = PublishedDocument.objects.get(original_id = orig_doc)
        except:
            orig_doc.has_been_published = True;
            orig_doc.save()
            current_doc = orig_doc.latest_id
    #        current_doc = Document.objects.filter(original_id=orig_doc, is_latest=True, is_edit=False)[0]
    #        Document.objects.filter(original_id=orig_doc).update(has_been_published=True)
            doc_text = current_doc.document_text
            doc_title = orig_doc.document_title
            u = orig_doc.user
            d = PublishedDocument(original_id=orig_doc, user=u, document_text=doc_text, document_title=doc_title, pub_date=timezone.now())
            d.save()
        pub.pendingArticles.remove(orig_doc)
        pub_date =PublicationDate(publication = pub, article = d)
        pub_date.save()
        pub.articles.add(d)
        pub.last_pub_date = d.pub_date
        text = pub_user.username + " published the document <b><a href='/browse/read/" + d.link_hash + "'>" + d.document_title + "</a></b> to the publication <b><a href='/browse/publication/" + pub_name + "'>" + pub_name + "</a></b><br>" + comment

    elif (submission_type == "Unlist"):
        d = PublishedDocument.objects.get(link_hash = hash_id)
        pub.articles.remove(d)
        text = pub_user.username + " unlisted the document <b><a href='/browse/read/" + d.link_hash + "'>" + d.document_title + "</a></b> from the publication <b><a href='/browse/publication/" + pub_name + "'>" + pub_name + "</a></b><br>" + comment
        
    elif (submission_type == "Reject"):
        d = Document.objects.get(link_hash = hash_id)
        pub.pendingArticles.remove(d)
        text = pub_user.username + " unlisted the document <b><a href='/browse/read/" + d.link_hash + "'>" + d.document_title + "</a></b> from the publication <b><a href='/browse/publication/" + pub_name + "'>" + pub_name + "</a></b><br>" + comment

    pub.save()
    
    if (pub_user != d.user):
        views.send_message_with_args(request, d.user.username, text, pub_user)
    
    return HttpResponse(d.link_hash)

def new_publication(request):
    pub_name = request.POST['new_publication_name']
    u = get_user(request)
    try:
        pub = Publication.objects.get(publication_name=pub_name)
        return HttpResponse("Publication already exists")
    except:
        pub = Publication(owner= u, publication_name = pub_name)
        pub.save()
        pub.editors.add(u)
        pub.writers.add(u)
        pub.save()
        return HttpResponseRedirect(reverse('publish:mydocs'))
        
def invite_member(request):
    pub_name = request.POST['publication_name']
    member_name = request.POST['username']
    pub = Publication.objects.get(publication_name=pub_name)
    u = User.objects.get(username=member_name)
    pub.writers.add(u)
    pub.save()
    return HttpResponse(member_name)
        
def change_permissions(request):
    pub_name = request.POST['publication_name']
    member_name = request.POST['memberPermissionSelect']
    submission_type = request.POST['submissionType']
    pub = Publication.objects.get(publication_name=pub_name)
    u = User.objects.get(username=member_name)
    if submission_type == "Remove Member":
        pub.editors.remove(u)
        pub.writers.remove(u)
    else:
        if 'canEdit' in request.POST:
            pub.editors.add(u)
        else:
            pub.editors.remove(u)
    pub.save()
    return HttpResponse(pub.publication_name)

def change_pub_type(request):
    pub_type = request.POST['pub_type']
    pub_name = request.POST['publication_name']
    pub = Publication.objects.get(publication_name=pub_name)
    if(pub_type == "open_publication"):
        pub.is_open = True;
    elif(pub_type == "open_submission"):
        pub.is_open = False;
        pub.accepts_articles = True;
    else:
        pub.is_open = False;
        pub.accepts_articles = False;
    pub.save()
    return HttpResponse(pub.publication_name)

def get_latest_submissions(request):
    pub_name = request.GET['publication_name']
    page = request.GET['page']
    pub = Publication.objects.get(publication_name=pub_name)
    pending_articles = pub.pendingArticles.all()

    paginator = Paginator(pending_articles, 30)
    try:
        returned_articles = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        returned_articles = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        returned_articles = paginator.page(paginator.num_pages)
        
    article_hashes = {}
    for article in returned_articles:
        sub_date = SubmissionDate.objects.get(publication = pub, article = article)
        article_hashes[article.document_title] = [article.link_hash, sub_date.date.strftime('%H:%M %Y-%m-%d '), article.user.username]
    context = {"pending_articles":article_hashes}
    return HttpResponse(json.dumps(context))

def get_latest_pubs(request):
    pub_name = request.GET['publication_name']
    page = request.GET['page']
    pub = Publication.objects.get(publication_name=pub_name)
    articles = pub.articles.all()

    paginator = Paginator(articles, 30)
    try:
        returned_articles = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        returned_articles = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        returned_articles = paginator.page(paginator.num_pages)
        
    article_hashes = {}
    for article in returned_articles:
        pub_date = PublicationDate.objects.filter(publication = pub, article = article).order_by('-date')[0]
        article_hashes[article.document_title] = [article.link_hash, pub_date.date.strftime('%H:%M %Y-%m-%d '), article.user.username]
    context = {"published_articles":article_hashes}
    return HttpResponse(json.dumps(context))

def add_sidebar(request):
    pub_id = request.POST['publication_id']
    sidebar_title = request.POST['title']
    sidebar_content = request.POST['content']
    pub = Publication.objects.get(pk=pub_id)
    s = Sidebar(title = sidebar_title, content = sidebar_content, publication = pub)
    s.save()
    return HttpResponse(s.content)
    