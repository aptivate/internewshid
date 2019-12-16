from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from dashboard.views import DashboardView
from hid.tabs.view_and_edit_table import view_and_edit_table_form_process_items

from .views.item import AddEditItemView
from .views.list_collection_types import ListCollectionTypes
from .views.upload_spreadsheet import UploadSpreadsheetView

urlpatterns = [
    url(r'^collection-types/upload/$', login_required(UploadSpreadsheetView.as_view()), name='collection-types-upload'),
    url(r'^collection-types/(?P<label>\w+)/$', login_required(ListCollectionTypes.as_view()), name='collection-types-edit'),
    url(r'^collection-types/$', login_required(ListCollectionTypes.as_view()), name='collection-types'),
    url(r'^process-items/$', login_required(view_and_edit_table_form_process_items), name="data-view-process"),
    url(r'^item/(?P<item_id>\d+)/edit/$', login_required(AddEditItemView.as_view()), name='edit-item'),
    url(r'^item/add/(?P<item_type>[-_\w]+)/$', login_required(AddEditItemView.as_view()), name='add-item'),
    url(r'^$', login_required(DashboardView.as_view()), name='dashboard'),
]
