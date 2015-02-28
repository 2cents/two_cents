from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.core.urlresolvers import reverse
from django.views import generic
from django.utils import timezone
from django import template

register = template.Library()

from django.contrib.auth import authenticate, login, logout, get_user

from browse.models import Document, EditRequest, Publication
from django.contrib.auth.models import User
# Create your views here.

def myedits(request):
    u = get_user(request)
    publication_list = Publication.objects.filter(editors=u)
    context = {'publication_list' : publication_list}
    return render(request, 'edit/myedits.html', context)

def edit(request, hash_id):
    doc = Document.objects.filter(link_hash=hash_id)[0]
    orig_doc = doc.original_id
    current_doc = Document.objects.filter(original_id=orig_doc, is_latest=True)[0]
    context = {'selected_doc': current_doc}
    return render(request, 'edit/index.html', context)