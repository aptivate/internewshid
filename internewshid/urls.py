from __future__ import absolute_import, unicode_literals

from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('users.auth_urls')),
    url(r'^api/', include('rest_api.urls')),
    url(r'^dashboard/', include('dashboard.urls')),
    url(r'^users/', include('users.urls')),
    url(r'^view-edit/', include('tabbed_page.urls')),
    url(r'^', include('hid.urls'))
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url('__debug__/', include(debug_toolbar.urls)),
    ]
