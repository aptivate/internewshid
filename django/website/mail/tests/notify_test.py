# coding=utf-8
from __future__ import unicode_literals

import os
import pytest
import mock
from django.test.utils import override_settings
from django.conf import settings
from django.core import mail as django_mail
from django.core.mail import EmailMessage
from mail import notify, DEFAULT_FROM


options = {
    'from_email': 'fake_from@aptivate.org',
    'to': ['recipient@aptivate.org', 'recipient2@aptivate.org'],
    'cc': ['recipient3@aptivate.org'],
    'bcc': ['hidden_santa@aptivate.org'],
    'subject': 'Hello',
    'body': 'Very short message'
}

TEST_TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.abspath(os.path.dirname(__file__)),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

def test_notify_sends_all_parameters():
    params = options.copy()

    assert len(django_mail.outbox) == 0
    notify(params)
    assert len(django_mail.outbox) == 1
    msg = django_mail.outbox[0]
    for key in params:
        assert getattr(msg, key) == params[key]


def test_notify_works_with_non_valid_parameters():
    params = options.copy()
    params.update({
        'junk': False
    })
    assert len(django_mail.outbox) == 0
    notify(params)
    assert len(django_mail.outbox) == 1


def test_notify_uses_default_from_when_missing_from_address():
    params = options.copy()
    del params['from_email']

    notify(params)
    msg = django_mail.outbox[0]
    assert msg.from_email == DEFAULT_FROM


@override_settings(TEMPLATES=TEST_TEMPLATES)
def test_notify_renders_template_referenced_by_name():
    template_name = 'test_email_template.html'
    params = options.copy()
    params['context'] = {'var': 'world'}
    params['template_name'] = template_name

    notify(params)
    msg = django_mail.outbox[0]
    assert msg.body == 'Hello world!\n'


def test_notify_renders_template_given_as_string():
    params = options.copy()
    params['context'] = {'var': 'world'}
    params['template_name'] = 'Hello {{ var }}!'

    notify(params)
    msg = django_mail.outbox[0]
    assert msg.body == 'Hello world!'


@pytest.fixture
def params():
    params = options.copy()
    params['context'] = {'var': 'world'}
    params['template_name'] = 'Hello {{ var }}!'
    return params


def test_passed_connection_get_used(params):
    connection = django_mail.get_connection()
    email = notify(params, connection=connection)
    assert email.connection == connection
