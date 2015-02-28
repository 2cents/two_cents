from django.conf.urls import patterns, url

from publish import views


urlpatterns = patterns('',
    url(r'^mydocs/$', views.mydocs, name='mydocs'),
    url(r'^new_publication/$', views.new_publication, name='new_publication'),
    url(r'^invite_member/$', views.invite_member, name='invite_member'),
    url(r'^change_permissions/$', views.change_permissions, name='change_permissions'),
    url(r'^publish_document_to_publication/$', views.publish_document_to_publication, name='publish_document_to_publication'),
    url(r'^publish_document/$', views.publish_document, name='publish_document'),
)