from django.conf import settings
from django.test.testcases import TestCase
from django.urls import reverse

from users.models import User

from .fast_dispatch import FastDispatchMixin


class SiteNeedsAuthenticationTests(FastDispatchMixin, TestCase):
    def test_dashboard_cant_be_accessed_when_not_logged_in(self):
        response = self.fast_dispatch('dashboard')
        self.assertEqual(settings.LOGIN_URL + '?next=' + reverse('dashboard'), response['Location'])

    def test_dashboard_can_be_accessed_when_logged_in(self):
        self.user = User()
        response = self.fast_dispatch('dashboard')

        response.render()

        self.assertEqual(response.template_name, ['dashboard/dashboard.html'])

    def test_logout_view_logs_user_out(self):
        self.user = User()

        self.fast_dispatch('dashboard')

        # The user when logged out should be None or AnonymousUser
        # We check that logout works by getting the user from the logout
        # request and using it as the user for the next one.
        response = self.fast_dispatch('logout')
        self.user = response.view.request.user

        response = self.fast_dispatch('dashboard')

        self.assertEqual(settings.LOGIN_URL + '?next=' + reverse('dashboard'), response['Location'])
