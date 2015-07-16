from django.conf.urls import patterns, url

from publish import views


urlpatterns = patterns('',
    url(r'^mydocs/$', views.mydocs, name='mydocs'),
    url(r'^new_publication/$', views.new_publication, name='new_publication'),
    url(r'^invite_member/$', views.invite_member, name='invite_member'),
    url(r'^get_latest_pubs/$', views.get_latest_pubs, name='get_latest_pubs'),
    url(r'^get_latest_submissions/$', views.get_latest_submissions, name='get_latest_submissions'),
    url(r'^change_permissions/$', views.change_permissions, name='change_permissions'),
    url(r'^change_pub_type/$', views.change_pub_type, name='change_pub_type'),
    url(r'^add_sidebar/$', views.add_sidebar, name='add_sidebar'),
    url(r'^publish_document_to_publication/$', views.publish_document_to_publication, name='publish_document_to_publication'),
    url(r'^publish_document/$', views.publish_document, name='publish_document'),
    url(r'^review/(?P<hash_id>.+)/$', views.review, name='review'),
    url(r'^unlist/$', views.unlist, name='unlist'),
    url(r'^$', views.mydocs, name='mydocs'),
)