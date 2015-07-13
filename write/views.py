from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.core.urlresolvers import reverse
from django.views import generic
from django.utils import timezone
from django import template

import requests
import lxml
from lxml import html

from django.core import serializers

import json
from datetime import datetime

import isbnlib

register = template.Library()

from django.contrib.auth import authenticate, login, logout, get_user

from browse.models import Document, EditRequest, Citation, Message, TwoCentsUser, DocumentDraft
from django.contrib.auth.models import User
from browse import views
# Create your views here.


def mydrafts(request):
    u = get_user(request)
    latest_document_list = Document.objects.filter(save_date__lte=timezone.now(), has_been_published=False).order_by('-save_date')[:16]
    context = {'latest_document_list': latest_document_list}
    return render(request, 'write/mydrafts.html', context)


def new(request):
    u = get_user(request)
    views.auth_redirect(u)
    doc_title = request.POST['doc_title']
    starter_html = request.POST['starter_html']
    if len(starter_html) > 0:
        new_doc_id = save_doc_in_db(request, starter_html, doc_title, "", "")
    else:
        new_doc_id = save_doc_in_db(request, "", doc_title, "", "")
    doc = Document.objects.get(pk=new_doc_id)
    return redirect('/write/' + doc.link_hash)


def revision(request, hash_id):
    doc = Document.objects.filter(link_hash=hash_id)[0]
#    orig_doc = doc.original_id
#    current_doc = Document.objects.filter(original_id=orig_doc, is_latest=True)[0]
    context = {'selected_doc': doc}
    return render(request, 'write/new.html', context)

def save_doc_in_db(request, doc_text, doc_title, doc_id, editorsString):    

    u = get_user(request)
    prev_doc = None
    try:
        orig_doc = Document.objects.get(pk=doc_id)
        prev_doc = orig_doc.latest_id
        new_version = prev_doc.document_version + 1
    except:
        orig_doc = Document(user=User.objects.get(pk=u.id), document_title=doc_title)
        orig_doc.save()
        new_version = 0

    if prev_doc is None or doc_text != prev_doc.document_text:
        DocumentDraft.objects.filter(document=orig_doc, is_latest=True).update(is_latest=False)
        d = DocumentDraft(document=orig_doc, document_text=doc_text, save_date=timezone.now(), is_latest=True, editors_list = editorsString, document_version = new_version)
    else:
        d = prev_doc

    d.save()
    orig_doc.latest_id = d
    orig_doc.save_date = d.save_date
    orig_doc.save()
    return orig_doc.id

def get_doc_version(request):
    doc_id = request.POST['doc_id']
    version = request.POST['version']
    d = DocumentDraft.objects.get(document = doc_id, document_version = version)
    context = {'draft_text' : d.document_text}
    return HttpResponse(json.dumps(context))
    
def request_edit(request):
    doc_text = request.POST['doc_text']
    doc_title = request.POST['doc_title']
    comment = request.POST['comment'].strip()
    editor_names = request.POST['editor_usernames']
    editors_list = editor_names.split(":")
    doc_id = request.POST['doc_id']
    
    new_doc_id = save_doc_in_db(request, doc_text, doc_title, doc_id, "")
    u = get_user(request)
    orig_doc = Document.objects.get(pk=new_doc_id)
    
    if comment != "":
        text = " requested edits to the document <b><a href='/edit/" + orig_doc.link_hash + "'>" + doc_title + "</a></b>:<br>" + comment
    else:
        text = " requested edits to the document <b><a href='/edit/" + orig_doc.link_hash + "'>" + doc_title + "</a></b>"
    
    failed_editors = []
    
    for editor_name in editors_list[:-1]:
        try:
            e = User.objects.get(username__iexact=editor_name)
            EditRequest.objects.filter(writer=u, editor=e, doc=orig_doc).delete()
            er = EditRequest(writer=u, editor=e, doc=orig_doc, request_date=timezone.now())
            er.save()
            full_text = u.username + text
            message = Message(sender = u, recipient = e, message_text = full_text, date=timezone.now())
            message.save()
            tcu = e.twocentsuser
            tcu.has_unread_message = True
            tcu.save()
        except:
            failed_editors.append(editor_name)
            
    return HttpResponse(failed_editors)

def get_editors_string(edit_count, editors):
    editorsList = editors.split(":")
    
    editorsString = ""
    
    if edit_count == "1":
        editorsString = edit_count + " edit from " + editorsList[0]
    elif len(editorsList) == 2:
        editorsString = edit_count + " edits from " + editorsList[0]
    elif len(editorsList) == 3:
        editorsString = edit_count + " edits from " + editorsList[0] + " and " + editorsList[1]
    elif len(editorsList) > 3:
        otherCount = len(editorsList) - 2
        editorsString = edit_count + " edits from " + editorsList[0] + ", " + editorsList[1] + " and " + otherCount + " others"
        
    return editorsString
    
    
def format_doc_text(text):
    text = text.strip()
    if (text.startswith("<p>") == False):
         first_part = text.split("<p>")[0]
         remainder = "<p>".join(text.split("<p>")[1:])
         if remainder != "":
             remainder = "<p>" + remainder
         text = "<p>" + first_part + "</p>" + remainder
    return text
    
def save_document(request):
    doc_text = request.POST['doc_text']
    doc_title = request.POST['doc_title']
    doc_id = request.POST['doc_id']
    edit_count = request.POST['edit_count']
    editors = request.POST.get('editors_dict', "")
    editorsString = get_editors_string(edit_count, editors)
    
    text = format_doc_text(doc_text)
        
    new_doc_id = save_doc_in_db(request, text, doc_title, doc_id, editorsString)
    return HttpResponse(new_doc_id)
    
def save_document_as_edit(request):
    u = get_user(request)
    doc_text = request.POST['doc_text']
    doc_title = request.POST['doc_title']
    doc_id = request.POST['doc_id']
    edit_count = request.POST['edit_count']
    editors = request.POST.get('editors_dict', "")
    editorsString = get_editors_string(edit_count, editors)
    
    text = format_doc_text(doc_text)
    
    orig_doc = Document.objects.get(pk=doc_id)
    author=orig_doc.user
    DocumentDraft.objects.filter(document=orig_doc, is_latest=True).update(is_latest=False)
    d = DocumentDraft(document=orig_doc, document_text=text, save_date=timezone.now(), is_edit=True, is_latest=True, edit_count=edit_count, editors_list = editorsString)
    d.save()
        
    orig_doc.latest_id = d
    orig_doc.save_date = d.save_date
    orig_doc.save()
    
    EditRequest.objects.filter(writer=author, editor= u, doc=orig_doc).delete()
    
    full_text = u.username + " submitted " + edit_count + " edits to the document <b><a href='/write/" + orig_doc.link_hash + "'>" + doc_title + "</a></b>"
    message = Message(sender = u, recipient = author, message_text = full_text, date=timezone.now())
    message.save()
    tcu = author.twocentsuser
    tcu.has_unread_message = True
    tcu.save()
    
    
    return HttpResponse(d.id)

def get_web_content(request):
    url = request.POST['url']
    source_type = request.POST['source_type']
    if source_type == "website":
        if url.startswith("http://") == False:
            url = "http://" + url
        r = requests.get(url)
        root = lxml.html.fromstring(r.content)
        description = "HELLO THERE"
        title = ""
        for tit in root.xpath("//meta[@property='og:title']"):
            title = tit.get("content")
        for tit in root.xpath("//meta[@name='title']"):
            title = tit.get("content")
        if title == "":
            for tit in reversed(root.xpath("//h1[@class='title']")):
                title = tit.text_content()
        if title == "":
            for tit in reversed(root.cssselect("title")):
                title = tit.text_content()

        author = "";
        for auth in root.xpath("//meta[@name='author']"):
            author = auth.get("content")
        if author == "":
            for auth in root.xpath("//a[@rel='author']"):
                author = auth.text_content()

        pub_date = ""

        site_name = ""
        for site in root.xpath("//meta[@property='og:site_name']"):
            site_name = site.get("content")

        return HttpResponse(json.dumps({"title" : title, "author" : author, "year" : pub_date, "publisher" : site_name}))

    else:
        isbn = ""
        if isbnlib.is_isbn10(url) or isbnlib.is_isbn13(url):
            isbn = url
        else:
            isbn = isbnlib.isbn_from_words(url)
        metaDict = None
        metaDict = isbnlib.meta(isbn, service='goob', cache=None)
        if metaDict is not None:
            author = metaDict.get("Authors")
            publisher = metaDict.get("Publisher")
            title = metaDict.get("Title")
            year = metaDict.get("Year")
            context = {'title': title, 'author':author, 'publisher':publisher, 'year':year}
            return HttpResponse(json.dumps(context))
        else:
            return HttpResponse("No book found")

def new_source(request):
    u = get_user(request)
    doc_id = request.POST['doc_id']
    orig_doc = Document.objects.get(pk=doc_id)
    new_source_type = request.POST['source_type']
    
    new_authors = request.POST.get("authors")
    new_title = request.POST.get("title")
    new_publisher = request.POST.get("publisher")
    new_pub_date = datetime.strptime(request.POST.get("pub_date"), "%m/%d/%Y")
    new_website = request.POST.get("website")
    
    citation = Citation(user = u, source_type = new_source_type, authors = new_authors, title = new_title, pub_date = new_pub_date, publisher = new_publisher, document = orig_doc)
    citation.save()
    
    c =  Citation.objects.get(id = citation.id)
    
    XMLSerializer = serializers.get_serializer("xml")
    xml_serializer = XMLSerializer()
    
    return HttpResponse(xml_serializer.serialize([c]))

def get_sources(request):
    u = get_user(request)
    doc_id = request.GET['doc_id']
    orig_doc = Document.objects.get(pk=doc_id)
    #orig_doc = doc.original_id
    citation_list = Citation.objects.filter(document = orig_doc)

    XMLSerializer = serializers.get_serializer("xml")
    xml_serializer = XMLSerializer()
    
    return HttpResponse(xml_serializer.serialize(citation_list))