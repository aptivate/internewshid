from django.core.urlresolvers import reverse

from rest_api.views import TaxonomyViewSet
from rest_framework.test import APIRequestFactory

actions = {'get': 'list'}
request_factory = APIRequestFactory()


def list_url():
    return reverse('taxonomy-list')


def get_view():
    return TaxonomyViewSet.as_view(actions)


def list(**kwargs):
    """ Return a list of Taxonomies

    If keyword arguments are given, they are used
    to filter the Taxonomies.
    """

    view = get_view()
    request = request_factory.get(list_url(), kwargs)
    return view(request).data
