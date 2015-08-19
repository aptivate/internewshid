from rest_api.views import TermViewSet
from rest_framework.test import APIRequestFactory
from rest_framework import status

from .exceptions import TransportException


request_factory = APIRequestFactory()


def get_view(actions):
    """ Return the view to perform the given action.

    Args:
        actions (dict): Dictionary of actions, eg.
            {'get': 'list'}
    Returns:
        View: A view object
    """
    return TermViewSet.as_view(actions)


def list(**kwargs):
    """ Return a list of Terms

    If keyword arguments are given, they are used
    to filter the terms. This can be used to list
    the terms in a given taxonomy.

    Args:
        **kwargs: Filters
    Returns:
        list: List of terms
    Raises:
        TransportException: On transport failure.
            'status_code' is set to the response
            status code.
    """
    view = get_view(actions={'get': 'list'})
    request = request_factory.get("", kwargs)
    response = view(request)

    if not status.is_success(response.status_code):
        response.data['status_code'] = response.status_code
        raise TransportException(response.data)

    return response.data
