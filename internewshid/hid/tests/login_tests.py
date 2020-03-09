from django.test import Client
from django.urls import reverse
from django.utils.six.moves.urllib.parse import urlsplit

import pytest

from users.models import User


@pytest.mark.django_db
def test_user_directed_to_login_page_when_csrf_error():
    business_email = 'william@example.com'
    password = 'passw0rd'

    User.objects.create_user(business_email, password)

    client = Client(enforce_csrf_checks=True)
    data = {'username': business_email,
            'password': password,
            'csrfmiddlewaretoken': 'notavalidtoken'}
    response = client.post(reverse('login'),
                           data=data, follow=True)

    assert hasattr(response, 'redirect_chain')
    assert len(response.redirect_chain) > 0, "Response didn't redirect"

    assert response.redirect_chain[0][1] == 302
    url, _ = response.redirect_chain[-1]
    scheme, netloc, path, query, fragment = urlsplit(url)
    assert path == reverse('login')

    url, _ = response.redirect_chain[-2]
    scheme, netloc, path, query, fragment = urlsplit(url)
    assert path == reverse('dashboard')

    assert response.status_code == 200
