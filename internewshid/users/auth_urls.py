from django.conf.urls import url
from django.contrib.auth.views import (
    LoginView, logout_then_login, PasswordChangeView, PasswordResetConfirmView
)
from django.urls import reverse

from .views import ResetPassword

urlpatterns = [
    url(r'login/$', LoginView.as_view(), name='login'),
    url(r'logout/$', logout_then_login, name='logout'),
    url(r'password_reset/$', ResetPassword.as_view(), name='password_reset'),
    url(r'password_reset_confirm/(?P<uidb64>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        PasswordResetConfirmView.as_view(), {'post_reset_redirect': '/'},
        name='password_reset_confirm'),
    url(r'password_change/$',
        PasswordChangeView.as_view(),
        {'post_change_redirect': reverse('personal_edit')},
        name='password_change'),
]
