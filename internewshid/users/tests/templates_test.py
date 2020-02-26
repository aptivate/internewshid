# coding=utf-8
import pytest

from ..views import UpdateContact
from .factories import ContactsManagerFactory, UserFactory


@pytest.mark.integration
@pytest.mark.groupfactory
@pytest.mark.django_db
def test_activation_email_link_is_rendered_if_contact_has_not_set_password(rf):
    view = UpdateContact.as_view()
    contact_for_editing = UserFactory()

    # I don't think we are using any of the code being tested here and...
    # * the code doesn't call User.objects.create_user()
    # * the tests don't call User.objects.create_user()
    # User.objects.create_user() would set a None password for us by default
    # which is interpreted as an unusable password
    # has_usable_password() changed in Django 2.1 re "no password set"
    # https://docs.djangoproject.com/en/2.2/ref/contrib/auth/#django.contrib.auth.models.User.has_usable_password  # noqa: E501
    contact_for_editing.set_password(None)
    contact_for_editing.save()
    request_user = ContactsManagerFactory()
    request = rf.get('/')
    request.user = request_user
    response = view(request, pk=contact_for_editing.id)
    response.render()
    assert 'Account not claimed' in str(response.content, 'utf-8')
    # The button name that triggers an activation email to be sent is the
    # save-and-email button - see views_test
    assert 'name="save-and-email"' in str(response.content, 'utf-8')


@pytest.mark.integration
@pytest.mark.groupfactory
@pytest.mark.django_db
def test_activation_email_link_is_not_rendered_if_contact_has_set_password(rf):
    view = UpdateContact.as_view()
    contact_for_editing = UserFactory()
    contact_for_editing.set_password('åρｒｏｐｅｒρäѕｓɰòｒｄ')
    contact_for_editing.save()
    request_user = ContactsManagerFactory()
    request = rf.get('/')
    request.user = request_user
    response = view(request, pk=contact_for_editing.id)
    response.render()
    assert 'Account not claimed' not in str(response.content, 'utf-8')
    # The button name that triggers an activation email to be sent is the
    # save-and-email button - see views_test
    assert 'name="save-and-email"' not in str(response.content, 'utf-8')
