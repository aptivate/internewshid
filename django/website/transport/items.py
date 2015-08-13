from django.core.urlresolvers import reverse
from django.utils.dateparse import parse_datetime
from rest_framework.test import APIRequestFactory
from rest_framework import status
from rest_api.serializers import ItemSerializer
from rest_api.views import ItemViewSet

from .exceptions import TransportException


actions = {
    'get': 'list',
    'post': 'create',
    'delete': 'destroy',
}
request_factory = APIRequestFactory()


def list_url():
    return reverse('item-list')


def detail_url(id):
    return reverse('item-detail', args=[id])


def get_view():
    return ItemViewSet.as_view(actions)


def _parse_date_fields(item):
    date_fields = ('created', 'timestamp')
    item_dict = dict(item)
    for date_field in date_fields:
        value = item_dict[date_field]
        if value is not None:
            item_dict[date_field] = parse_datetime(value)
    return item_dict


def list(**kwargs):
    """ Return a list of Items

    If keyword arguments are given, they are used
    to filter the Items.
    """
    # FIXME: currently only body exact filtering is supported
    view = get_view()
    request = request_factory.get(list_url(), kwargs)

    items = view(request).data

    serializer = ItemSerializer(data=items, many=True)

    if serializer.is_valid():
        return serializer.validated_data

    raise TransportException(serializer.errors)


def create(item):
    """ Create an Item from the given dict """
    view = get_view()
    request = request_factory.post(list_url(), item)
    response = view(request)
    if status.is_success(response.status_code):
        return response.data
    else:
        response.data['status_code'] = response.status_code
        raise TransportException(response.data)


def delete(id):
    """ Delete the Item wit the given ID """
    view = get_view()
    request = request_factory.delete(detail_url(id))
    return view(request, pk=id)


def bulk_delete(ids):
    """ Delete all Items whose ids appear in the given list """
    # DELETE http requests appear not to send query parameters so
    # for the moment I'm mapping this onto multiple calls to delete()
    for id in ids:
        delete(id)


def add_term_url(item_id):
    return reverse('item-add-term', kwargs={'pk': item_id})


def add_term(item_id, taxonomy_slug, name):
    """ Add term named `name` within the Taxonomy with `taxonomy_slug` to the
    Item with id `item_id`

    args:
        item_id: e.g. 67
        taxonomy_slug: e.g. 'ebola-questions'
        name: name of a Term in the Taxonomy with given slug

    returns:
        response from the server

    raises:
       TransportException on failure

    For the moment both the taxonomy and term must already exist.
    """
    view = ItemViewSet.as_view(actions={'post': 'add_term'})

    term = {'taxonomy': taxonomy_slug, 'name': name}
    request = request_factory.post(add_term_url(item_id), term)
    response = view(request, item_pk=item_id)

    if status.is_success(response.status_code):
        return response.data
    else:
        response.data['status_code'] = response.status_code
        response.data['term'] = term
        response.data['item_id'] = item_id
        raise TransportException(response.data)


def delete_all_terms_url(item_id):
    return reverse('item-delete-all-terms', kwargs={'pk': item_id})


def delete_all_terms(item_id, taxonomy_slug):
    view = ItemViewSet.as_view(actions={'post': 'delete_all_terms'})

    taxonomy = {'taxonomy': taxonomy_slug}
    request = request_factory.post(delete_all_terms_url(item_id), taxonomy)
    response = view(request, item_pk=item_id)

    if not status.is_success(response.status_code):
        response.data['status_code'] = response.status_code
        raise TransportException(response.data)

    return response.data
