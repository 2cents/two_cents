from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'two_cents.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^browse/', include('browse.urls', namespace="browse")),
    url(r'^publish/', include('publish.urls', namespace="publish")),
    url(r'^write/', include('write.urls', namespace="write")),
    url(r'^edit/', include('edit.urls', namespace="edit")),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', include('browse.urls', namespace="browse")),
)
