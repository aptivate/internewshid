from django.conf.urls import patterns, url
from django.contrib.auth.views import login
from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required

from .views import UploadSpreadsheetView, ListSources


urlpatterns = patterns('',
    url(r'^sources/upload/$', login_required(UploadSpreadsheetView.as_view()), name='sources-upload'),
    url(r'^sources/(?P<label>\w+)/$', login_required(ListSources.as_view()), name='sources-edit'),
    url(r'^sources/$', login_required(ListSources.as_view()), name='sources'),
    url(r'^view/$', login_required(TemplateView.as_view(template_name='hid/view.html')), name="data-view"),
    url(r'^$', login_required(TemplateView.as_view(template_name='hid/dashboard.html')), name="dashboard"),
)
