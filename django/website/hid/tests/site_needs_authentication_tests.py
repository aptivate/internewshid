from django.conf import settings
from django.core.urlresolvers import reverse
from django.test.testcases import SimpleTestCase

from .fast_dispatch import FastDispatchMixin
from users.models import User


class SiteNeedsAuthenticationTests(FastDispatchMixin, SimpleTestCase):
    def test_index_page_cant_be_accessed_when_not_logged_in(self):
        response = self.fast_dispatch('dashboard')
        self.assertEqual(settings.LOGIN_URL + '?next=' + reverse('dashboard'), response['Location'])

    def test_index_page_can_be_accessed_when_logged_in(self):
        self.user = User()
        response = self.fast_dispatch('dashboard')

        response.render()

        self.assertIn('dashboard', response.content)
