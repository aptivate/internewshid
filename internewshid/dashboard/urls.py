from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from dashboard.views import DashboardView

urlpatterns = [
    url(r'^(?P<name>.*)$', login_required(DashboardView.as_view()))
]
