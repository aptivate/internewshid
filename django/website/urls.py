from __future__ import unicode_literals, absolute_import

from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns
from django.views.generic.base import RedirectView

from django.contrib import admin
from django.conf import settings


urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('users.auth_urls')),
    url(r'^api/', include('rest_api.urls')),
    url(r'^dashboard/', include('dashboard.urls')),
    url(r'^users/', include('users.urls')),
    url(r'^view-edit/', include('tabbed_page.urls')),
    url(r'^', include('hid.urls'))
]
