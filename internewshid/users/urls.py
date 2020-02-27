from django.conf.urls import url

from .views import (
    AddContact, DeleteContact, ListContacts, SendActivationEmailView,
    UpdateContact, UpdatePersonalInfo
)

urlpatterns = [
    url(r'edit/$', AddContact.as_view(), name='contact_add'),
    url(r'edit/(?P<pk>\d+)/$', UpdateContact.as_view(),
        name='contact_update'),
    url(r'delete/(?P<pk>\d+)/$', DeleteContact.as_view(),
        name='contact_delete'),
    url(r'activate/(?P<pk>\d+)/$', SendActivationEmailView.as_view(permanent=True),
        name='contact_claim_account'),
    url(r'personal/$', UpdatePersonalInfo.as_view(), name='personal_edit'),
    url(r'$', ListContacts.as_view(), name='contact_list'),
]
