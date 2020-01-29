from django.conf.urls import url
from django.contrib.auth.views import (
    LoginView, PasswordResetConfirmView, logout_then_login
)

from .views import ResetPassword

urlpatterns = [
    url(r'login/$', LoginView.as_view(), name='login'),
    url(r'logout/$', logout_then_login, name='logout'),
    url(r'password_reset/$', ResetPassword.as_view(), name='password_reset'),
    url(r'password_reset_confirm/(?P<uidb64>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        PasswordResetConfirmView.as_view(), {'post_reset_redirect': '/'},
        name='password_reset_confirm'),
]
