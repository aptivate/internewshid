from rest_api.views import TaxonomyViewSet
from rest_framework.test import APIRequestFactory
from rest_framework import status

from .exceptions import TransportException
from .terms import list as terms_list

request_factory = APIRequestFactory()


def get_view(actions):
    return TaxonomyViewSet.as_view(actions)


def list(**kwargs):
    """ Return a list of Taxonomies

    If keyword arguments are given, they are used
    to filter the Taxonomies.
    """

    view = get_view(actions={'get': 'list'})
    request = request_factory.get("", kwargs)
    return view(request).data


def _add_zero_counts_for_missing_terms(slug, itemcounts):
    # We want to return zero counts for terms that fall outside the date range,
    # which the API doesn't do for us. So we need to get all the terms for the
    # taxonomy and set any that aren't in the date range results to count: 0
    all_terms = terms_list(taxonomy=slug)

    itemcounts_by_name = {t['name']: t for t in itemcounts}

    new_itemcounts = []

    for term in all_terms:
        if term['name'] not in itemcounts_by_name:
            term['count'] = 0
        else:
            term = itemcounts_by_name[term['name']]

        new_itemcounts.append(term)

    return new_itemcounts


def term_itemcount(slug, **kwargs):
    view = get_view(actions={'get': 'itemcount'})
    request = request_factory.get("", kwargs)
    response = view(request, slug=slug)

    if not status.is_success(response.status_code):
        response.data['status_code'] = response.status_code
        raise TransportException(response.data)

    if 'start_time' not in kwargs or 'end_time' not in kwargs:
        return response.data

    return _add_zero_counts_for_missing_terms(slug, response.data)
