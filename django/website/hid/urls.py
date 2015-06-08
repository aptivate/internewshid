from django.conf.urls import patterns, url
from django.contrib.auth.views import login
from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required


urlpatterns = patterns('',
    url(r'^$', login_required(TemplateView.as_view(template_name='hid/dashboard.html')), name="dashboard"),
)
