from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from .views import TabbedPageView

urlpatterns = [
    url(r'^(?P<name>[^/]*)(/(?P<tab_name>.*))?$',
        TabbedPageView.as_view(),
        name='tabbed-page')
]
