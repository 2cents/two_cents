from django.conf.urls import patterns, url

from edit import views


urlpatterns = patterns('',
    url(r'^myedits/$', views.myedits, name='myedits'),
    url(r'^(?P<hash_id>.+)$', views.edit_draft, name='edit_draft'),
    url(r'^$', views.myedits, name='myedits'),
)