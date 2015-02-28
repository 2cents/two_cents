from django.conf.urls import patterns, url

from write import views


urlpatterns = patterns('',
 #   url(r'^register/$', 'django.contrib.auth.views.login', {'template_name': 'browse/login.html'}),
#    url(r'^login/$', views.login_form, name='login'),
#    url(r'^logout/$', views.logout_view, name='logout'),
    url(r'^save_document_as_edit/$', views.save_document_as_edit, name='save_document_as_edit'),
    url(r'^save_document/$', views.save_document, name='save_document'),
    url(r'^request_edit/$', views.request_edit, name='request_edit'),
    url(r'^new/$', views.new, name='new'),
    url(r'^new_source/$', views.new_source, name='new_source'),
    url(r'^get_sources/$', views.get_sources, name='get_sources'),
    url(r'^new/get_web_content$', views.get_web_content, name='get_web_content'),
    url(r'^(?P<hash_id>.+)$', views.revision, name='revision'),
    url(r'^$', views.mydrafts, name='mydrafts'),
)