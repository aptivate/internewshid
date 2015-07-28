from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from dashboard.views import DashboardView

from .views import (
    UploadSpreadsheetView, ListSources, ViewItems, ViewSingleItem, EditSingleItem, process_items
)

urlpatterns = patterns('',
    url(r'^sources/upload/$', login_required(UploadSpreadsheetView.as_view()), name='sources-upload'),
    url(r'^sources/(?P<label>\w+)/$', login_required(ListSources.as_view()), name='sources-edit'),
    url(r'^sources/$', login_required(ListSources.as_view()), name='sources'),
    url(r'^view/process/$', login_required(process_items), name="data-view-process"),
    url(r'^view/$', login_required(ViewItems.as_view()), name="data-view"),
    url(r'^view/(?P<id>\d+)$', login_required(ViewSingleItem.as_view())),
    url(r'^view/(?P<id>\d+)/edit$', login_required(EditSingleItem.as_view())),
    url(r'^$', login_required(DashboardView.as_view()), name='dashboard')
)
