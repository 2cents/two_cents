from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.core.urlresolvers import reverse
from django.views import generic
from django.utils import timezone
from django import template

register = template.Library()

from django.contrib.auth import authenticate, login, logout, get_user

from browse.models import Document, PublishedDocument, EditRequest, Publication
from django.contrib.auth.models import User
# Create your views here.

def mydocs(request):
    u = get_user(request)
    publication_list = Publication.objects.filter(editors=u)
    write_member_list = Publication.objects.filter(writers=u)
    context = {'publication_list': publication_list, 'write_member_list': write_member_list}
    return render(request, 'publish/mydocs.html', context)

def publish_document(request):
    submission_type = request.POST['submissionType']
    hash_id = request.POST['docHash']
    doc = Document.objects.filter(link_hash=hash_id)[0]
    if submission_type == "Publish":
        return(publish_document_to_publication(request))
    elif submission_type == "Submit to Publication":
        pub_name = request.POST['submit_publication_name']
        pub = Publication.objects.get(publication_name=pub_name)
        orig_doc = doc.original_id
        pub.pendingArticles.add(orig_doc)
        pub.save()
    else:
        orig_doc = doc.original_id
        try:
            current_pub = PublishedDocument.objects.get(original_id = orig_doc)
        except:
            orig_doc.has_been_published = True;
            orig_doc.save()
            current_doc = Document.objects.filter(original_id=orig_doc, is_latest=True, is_edit=False)[0]
            Document.objects.filter(original_id=orig_doc).update(has_been_published=True)
            doc_text = current_doc.document_text
            doc_title = current_doc.document_title
            u = current_doc.user
            d = PublishedDocument(original_id=orig_doc, user=u, document_text=doc_text, document_title=doc_title, pub_date=timezone.now())
            d.save()
            tcu = u.twocentsuser
            tcu.last_pub_date = d.pub_date
            tcu.save()

    return HttpResponseRedirect(reverse('browse:index'))

def publish_document_to_publication(request):
    hash_id = request.POST['docHash']
    doc = Document.objects.get(link_hash=hash_id)
    pub_name = request.POST['publication_name']
    pub = Publication.objects.get(publication_name=pub_name)
    orig_doc = doc.original_id
    try:
        d = PublishedDocument.objects.get(original_id = orig_doc)
    except:
        orig_doc.has_been_published = True;
        orig_doc.save()
        current_doc = Document.objects.filter(original_id=orig_doc, is_latest=True, is_edit=False)[0]
        Document.objects.filter(original_id=orig_doc).update(has_been_published=True)
        doc_text = current_doc.document_text
        doc_title = current_doc.document_title
        u = current_doc.user
        d = PublishedDocument(original_id=orig_doc, user=u, document_text=doc_text, document_title=doc_title, pub_date=timezone.now())
        d.save()
    pub.pendingArticles.remove(doc)
    pub.articles.add(d)
    pub.last_pub_date = d.pub_date
    pub.save()
    return HttpResponseRedirect(reverse('browse:index'))

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
    return HttpResponse(pub.publication_name)
        
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