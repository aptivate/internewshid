from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from .views import TabbedPageView

urlpatterns = [
    url(r'^/$', login_required(TabbedPageView.as_view())),
    url(r'^(?P<name>\w+)/$', login_required(TabbedPageView.as_view())),
    url(r'^(?P<name>\w+)/(?P<tab_name>\w+)/$',
        login_required(TabbedPageView.as_view()),
        name='tabbed-page')
]
