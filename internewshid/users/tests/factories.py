# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import Group

import factory

from ..group_permissions import GroupPermissions
from ..models import User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    # must be unique so we specify and increase
    business_email = factory.Sequence(lambda n: "email%d@test.com" % n)
    first_name = factory.Sequence(lambda n: u"ｆíｒѕｔ %d" % n)
    last_name = factory.Sequence(lambda n: u"ｌåｓｔɭａｓｔ %d" % n)

    # Other required fields (you will still need to handle password
    # yourself depending on what you want to do
    gender = 'female'
    contact_type = u"ｃòлｔáｃｔ ｔｙｐé"
    title = u"ｔïｔｌë"


def ContactsManagerFactory():
    group_name = 'Contacts Managers'
    try:
        group = Group.objects.get(name=group_name)
    except Group.DoesNotExist:
        # Don't run it if we don't have to (e.g. calling factory more than
        # once per test)
        GroupPermissions()._add_contacts_managers_permissions()
        group = Group.objects.get(name=group_name)
    user = UserFactory()
    user.groups.add(group)
    return user