from django.core.urlresolvers import reverse

from rest_api.views import TaxonomyViewSet
from rest_framework.test import APIRequestFactory

request_factory = APIRequestFactory()


def list_url():
    return reverse('taxonomy-list')


def itemcount_url(slug):
    return reverse('taxonomy-itemcount', kwargs={'slug': slug})


def get_view(actions):
    return TaxonomyViewSet.as_view(actions)


def list(**kwargs):
    """ Return a list of Taxonomies

    If keyword arguments are given, they are used
    to filter the Taxonomies.
    """

    view = get_view(actions={'get': 'list'})
    request = request_factory.get(list_url(), kwargs)
    return view(request).data


def term_itemcount(slug):
    view = get_view(actions={'get': 'itemcount'})
    request = request_factory.get(itemcount_url(slug))
    return view(request, slug=slug).data
