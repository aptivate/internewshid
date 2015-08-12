from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from dashboard.views import DashboardView

from .views.upload_spreadsheet import UploadSpreadsheetView
from .views.list_sources import ListSources
from .views.item import AddEditItem

from hid.tabs.view_and_edit_table import view_and_edit_table_form_process_items

urlpatterns = patterns('',
    url(r'^sources/upload/$', login_required(UploadSpreadsheetView.as_view()), name='sources-upload'),
    url(r'^sources/(?P<label>\w+)/$', login_required(ListSources.as_view()), name='sources-edit'),
    url(r'^sources/$', login_required(ListSources.as_view()), name='sources'),
    url(r'^process-items/$', login_required(view_and_edit_table_form_process_items), name="data-view-process"),
    url(r'^item/(?P<id>\d+)/edit/$', login_required(AddEditItem.as_view())),
    url(r'^item/new/$', login_required(AddEditItem.as_view())),
    url(r'^$', login_required(DashboardView.as_view()), name='dashboard'),
)
