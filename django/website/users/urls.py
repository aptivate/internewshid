from django.conf.urls import patterns, url
from django.contrib.auth.views import login


urlpatterns = patterns('',
    url(r'login/$', login, name="login"),
)
