from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic.base import RedirectView
from django.contrib import admin
admin.autodiscover()

from smrt.views import SmrtView

urlpatterns = patterns('',
    url(r'^/admin/?', include(admin.site.urls)),
    url(r'^favicon\.ico$', RedirectView.as_view(url='/static/favicon.ico')),
    url(r'^/?', SmrtView.as_view()),
)
urlpatterns += staticfiles_urlpatterns()