from django.conf.urls import patterns, url
from django.contrib.auth.views import login, logout


urlpatterns = patterns('',
    url(r'login/$', login, name="login"),
    url(r'logout/$', login, name="logout"),
)
