from datetime import datetime

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.test import RequestFactory
from django.urls import reverse
from django.utils import timezone

import pytest
from mock import Mock, patch

import transport
from chn_spreadsheet.tests.conftest import taxonomies  # noqa
from hid.constants import ITEM_TYPE_CATEGORY
from taxonomies.models import Taxonomy
from taxonomies.tests.factories import TaxonomyFactory, TermFactory
from transport.exceptions import TransportException

from ..views.item import DEFAULT_ITEM_TYPE, AddEditItemView
from .views_tests import assert_message, assert_no_messages, fix_messages


@pytest.fixture
def item_type_taxonomy():
    # TODO: Rename this. This is the taxonomy used to categories items
    # not the taxonomy called 'item-types'
    slug = ITEM_TYPE_CATEGORY['all']

    try:
        taxonomy = Taxonomy.objects.get(slug=slug)
    except Taxonomy.DoesNotExist:
        taxonomy = Taxonomy.objects.create(name=slug)

    return taxonomy


@pytest.fixture
def item():
    msg = {
        'body': "What is the cuse of Ebola?",
        'timestamp': "2015-02-23 00:00:00",
    }
    response = transport.items.create(msg)

    return response


@pytest.fixture
def item_type():
    return {'name': 'question', 'long_name': 'Question'}


@pytest.fixture
def add_view(item_type):
    view = AddEditItemView()
    view.item_type = item_type

    url = reverse('add-item', kwargs={'item_type': item_type['name']})

    factory = RequestFactory()
    view.request = factory.post(url)
    view.request = fix_messages(view.request)

    return view


@pytest.fixture
def view(item, item_type):
    view = AddEditItemView()
    view.item = item
    view.item_type = item_type

    url = reverse('edit-item',
                  kwargs={'item_id': item['id']})

    factory = RequestFactory()
    view.request = factory.post(url)
    view.request = fix_messages(view.request)

    return view


@pytest.fixture
def new_form(view):
    form = view.form_class('question')
    form.cleaned_data = {
        'id': 0,
    }

    form.cleaned_data['next'] = '/'

    return form


@pytest.fixture
def update_form(view):
    form = view.form_class('question')
    form.cleaned_data = {
        'id': view.item['id'],
        'timestamp': view.item['timestamp'],
    }
    form.cleaned_data['next'] = '/'

    return form


ReqFactory = RequestFactory()


def get_view_for_request(view_class, url_name, args=None, kwargs=None,
                         request_type='get', post=None, get=None):
    """ Instantiate a class based view for the given request, and
        return the view object

        Args:
            view_class (Class): Class of the view
            url_name (str): Name of the url to request
            args (list): Arguments passed to reverse
            kwargs (dict): Arguments passed to reverse
            request_type (str): Type of query. Either 'get' or 'post'
            post (dict): Arguments passed to post requests
            get (dict): Arguemnts passed to get requests
        Returns:
            object: The instanced view object
    """
    if args is None:
        args = []
    if kwargs is None:
        kwargs = {}
    if post is None:
        post = {}
    if get is None:
        get = {}

    url = reverse(url_name, args=args, kwargs=kwargs)
    if request_type == 'get':
        request = ReqFactory.get(url, get)
    else:
        request = ReqFactory.post(url, post)
    request = fix_messages(request)
    view = view_class()
    view.request = request
    view.args = args
    view.kwargs = kwargs
    return view


def make_request(view_class, url_name, args=None, kwargs=None,
                 request_type='get', post=None, get=None):
    """ Perform the given request, and return the view and the response.

        Args:
            See get_view_for_request
        Returns:
            (view, response) tuple
    """
    view = get_view_for_request(view_class, url_name, args, kwargs,
                                request_type, post, get)
    if request_type == 'get':
        response = view.get(view.request, *view.args, **view.kwargs)
    else:
        response = view.post(view.request, *view.args, **view.kwargs)

    return (view, response)


@pytest.fixture
def generic_item():
    return {
        'id': 1001,
        'body': 'hello',
        'created': datetime(2015, 5, 5),
        'timestamp': datetime(2016, 6, 6),
        'last_updated': datetime(2017, 7, 7),
        'terms': [
            {
                'taxonomy': 'item-types',
                'name': 'generic',
                'long_name': 'Generic'
            },
            {
                'taxonomy': 'a-taxonomy',
                'name': 'a-term',
                'long_name': 'A Term'
            }
        ]
    }


@pytest.fixture
def item_without_item_type():
    return {
        'id': 1001,
        'body': 'hello',
        'created': datetime(2015, 5, 5),
        'timestamp': datetime(2016, 6, 6),
        'last_updated': datetime(2017, 7, 7),
        'terms': []
    }


@pytest.fixture
def an_item_type():
    return {
        'taxonomy': 'item-types',
        'name': 'an-item-type',
        'long_name': 'An Item Type'
    }


@pytest.mark.django_db
def test_the_item_is_added_to_the_view_on_get_requests(generic_item):
    with patch('hid.views.item.transport.items.get') as get_item:
        get_item.return_value = generic_item
        (view, response) = make_request(
            AddEditItemView,
            'edit-item',
            kwargs={'item_id': 103}
        )

    assert view.item == generic_item


@pytest.mark.django_db
def test_the_item_type_is_added_to_the_view_on_get_requests(generic_item):
    with patch('hid.views.item.transport.items.get') as get_item:
        get_item.return_value = generic_item
        (view, response) = make_request(
            AddEditItemView,
            'edit-item',
            kwargs={'item_id': 103}
        )

    assert view.item_type['name'] == 'generic'


@pytest.mark.django_db
def test_there_is_a_default_item_type_on_get_requests(item_without_item_type):
    default_item_type = {
        'name': 'a-default-type',
        'long_name': 'A Default Type',
        'taxonomy': 'item-types'
    }

    with patch.dict(DEFAULT_ITEM_TYPE, default_item_type):
        with patch('hid.views.item.transport.items.get') as get_item:
            get_item.return_value = item_without_item_type
            (view, response) = make_request(
                AddEditItemView,
                'edit-item',
                kwargs={'item_id': 103}
            )

        assert view.item_type == default_item_type


@pytest.mark.django_db
def test_the_item_terms_are_added_to_the_view_on_get_requests(generic_item):
    with patch('hid.views.item.transport.items.get') as get_item:
        get_item.return_value = generic_item
        (view, response) = make_request(
            AddEditItemView,
            'edit-item',
            kwargs={'item_id': 103}
        )

    assert view.item_terms == {
        'item-types': [{
            'taxonomy': 'item-types',
            'name': 'generic',
            'long_name': 'Generic'
        }],
        'a-taxonomy': [{
            'taxonomy': 'a-taxonomy',
            'name': 'a-term',
            'long_name': 'A Term'
        }]
    }


@pytest.mark.django_db
def test_the_item_is_added_to_the_view_on_post_requests(generic_item):
    with patch('hid.views.item.transport.items.get') as get_item:
        get_item.return_value = generic_item
        (view, response) = make_request(
            AddEditItemView,
            'edit-item',
            kwargs={'item_id': 103},
            request_type='post',
            post={
                'action': 'cancel',
                'next': ''
            }
        )

    assert view.item == generic_item


@pytest.mark.django_db
def test_the_item_type_is_added_to_the_view_on_post_requests(generic_item):
    with patch('hid.views.item.transport.items.get') as get_item:
        get_item.return_value = generic_item
        (view, response) = make_request(
            AddEditItemView,
            'edit-item',
            kwargs={'item_id': 103},
            request_type='post',
            post={
                'action': 'cancel',
                'next': ''
            }
        )

    assert view.item_type['name'] == 'generic'


@pytest.mark.django_db
def test_there_is_a_default_item_type_on_post_requests(item_without_item_type):
    default_item_type = {
        'name': 'a-default-type',
        'long_name': 'A Default Type',
        'taxonomy': 'item-types'
    }

    with patch.dict(DEFAULT_ITEM_TYPE, default_item_type):
        with patch('hid.views.item.transport.items.get') as get_item:
            get_item.return_value = item_without_item_type
            (view, response) = make_request(
                AddEditItemView,
                'edit-item',
                kwargs={'item_id': 103},
                request_type='post',
                post={
                    'action': 'cancel',
                    'next': ''
                }
            )

        assert view.item_type == default_item_type


@pytest.mark.django_db
def test_the_item_terms_are_added_to_the_view_on_post_requests(generic_item):
    with patch('hid.views.item.transport.items.get') as get_item:
        get_item.return_value = generic_item
        (view, response) = make_request(
            AddEditItemView,
            'edit-item',
            kwargs={'item_id': 103},
            request_type='post',
            post={
                'action': 'cancel',
                'next': ''
            }
        )

    assert view.item_terms == {
        'item-types': [{
            'taxonomy': 'item-types',
            'name': 'generic',
            'long_name': 'Generic'
        }],
        'a-taxonomy': [{
            'taxonomy': 'a-taxonomy',
            'name': 'a-term',
            'long_name': 'A Term'
        }]
    }


@pytest.mark.django_db
def test_form_initial_values_set_that_of_item(generic_item):
    with patch('hid.views.item.transport.items.get') as get_item:
        get_item.return_value = generic_item
        (view, response) = make_request(
            AddEditItemView,
            'edit-item',
            kwargs={'item_id': 103}
        )

    initial = view.get_initial()
    assert initial['id'] == 1001
    assert initial['body'] == 'hello'
    assert initial['timestamp'] == datetime(2016, 6, 6)


@pytest.mark.django_db
def test_form_next_url_is_next_query_parameter(generic_item):
    with patch('hid.views.item.transport.items.get') as get_item:
        get_item.return_value = generic_item
        (view, response) = make_request(
            AddEditItemView,
            'edit-item',
            kwargs={'item_id': 103},
            get={'next': 'http://example.com'}
        )

    initial = view.get_initial()
    assert initial['next'] == 'http://example.com'


@pytest.mark.django_db
def test_form_next_url_is_referer_if_no_next_query_parameter(generic_item):
    with patch('hid.views.item.transport.items.get') as get_item:
        get_item.return_value = generic_item
        (view, response) = make_request(
            AddEditItemView,
            'edit-item',
            kwargs={'item_id': 103}
        )

    view.request.META['HTTP_REFERER'] = '/view-edit/main/rumors'

    initial = view.get_initial()
    assert initial['next'] == '/view-edit/main/rumors'


@pytest.mark.django_db
def test_form_next_url_is_dashboard_if_nothing_else_set(generic_item):
    with patch('hid.views.item.transport.items.get') as get_item:
        get_item.return_value = generic_item
        (view, response) = make_request(
            AddEditItemView,
            'edit-item',
            kwargs={'item_id': 103}
        )

    initial = view.get_initial()
    assert initial['next'] == reverse('dashboard')


@pytest.mark.django_db
def test_context_data_includes_the_item(generic_item):
    with patch('hid.views.item.transport.items.get') as get_item:
        get_item.return_value = generic_item
        (view, response) = make_request(
            AddEditItemView,
            'edit-item',
            kwargs={'item_id': 103},
        )

    assert 'item' in response.context_data
    assert response.context_data['item']['id'] == 1001


@pytest.mark.django_db
def test_context_data_includes_item_type_label(generic_item):
    with patch('hid.views.item.transport.items.get') as get_item:
        get_item.return_value = generic_item
        (view, response) = make_request(
            AddEditItemView,
            'edit-item',
            kwargs={'item_id': 103},
        )

    assert 'item_type_label' in response.context_data
    assert response.context_data['item_type_label'] == 'Generic'


@pytest.mark.django_db
def test_correct_item_is_fetched_during_request(generic_item):
    with patch('hid.views.item.transport.items.get') as get_item:
        get_item.return_value = generic_item
        make_request(
            AddEditItemView,
            'edit-item',
            kwargs={'item_id': 103},
        )

    (args, _) = get_item.call_args
    assert get_item.called
    assert args[0] == 103


@pytest.mark.django_db
def test_displaying_existing_item_returns_template_response(generic_item):
    with patch('hid.views.item.transport.items.get') as get_item:
        get_item.return_value = generic_item
        (view, response) = make_request(
            AddEditItemView,
            'edit-item',
            kwargs={'item_id': 103},
        )

    assert type(response) is TemplateResponse


def test_displaying_unknown_item_returns_redirect_response(generic_item):
    with patch('hid.views.item.transport.items.get') as get_item:
        get_item.side_effect = TransportException({})
        get_item.return_value = generic_item
        (view, response) = make_request(
            AddEditItemView,
            'edit-item',
            kwargs={'item_id': 103},
        )

    assert type(response) is HttpResponseRedirect


def test_add_new_item_get_request_populates_item_type(an_item_type):
    with patch('hid.views.item.transport.terms.list') as list_term:
        list_term.return_value = [an_item_type]
        (view, response) = make_request(
            AddEditItemView,
            'add-item',
            kwargs={'item_type': 'an-item-type'},
        )

    assert view.item_type == an_item_type


def test_add_new_item_post_request_populates_item_type(an_item_type):
    with patch('hid.views.item.transport.terms.list') as list_term:
        list_term.return_value = [an_item_type]
        (view, response) = make_request(
            AddEditItemView,
            'add-item',
            kwargs={'item_type': 'an-item-type'},
            request_type='post',
            post={
                'action': 'save',
                'next': ''
            }
        )

    assert view.item_type == an_item_type


def test_add_new_item_returns_template_response(an_item_type):
    with patch('hid.views.item.transport.terms.list') as list_term:
        list_term.return_value = [an_item_type]
        (view, response) = make_request(
            AddEditItemView,
            'add-item',
            kwargs={'item_type': 'an-item-type'},
        )

    assert type(response) is TemplateResponse


def test_add_new_item_with_unknown_item_type_redirects():
    with patch('hid.views.item.transport.terms.list') as list_term:
        list_term.return_value = []
        (view, response) = make_request(
            AddEditItemView,
            'add-item',
            kwargs={'item_type': 'an-item-type'},
        )

    assert type(response) is HttpResponseRedirect


@pytest.mark.django_db
def test_submitting_form_with_id_equal_0_creates_an_item(item_type):
    body = 'Hello, here is a new item'
    the_time = datetime(2015, 6, 27, 0, 0)
    (view, response) = make_request(
        AddEditItemView,
        'add-item',
        kwargs={'item_type': item_type['name']},
        request_type='post',
        post={
            'action': 'save',
            'timestamp': the_time,
            'next': '/',
            'id': 0,
            'body': body
        }
    )

    assert view.item['id'] > 0
    item = transport.items.get(view.item['id'])
    assert item is not None


@pytest.mark.django_db
def test_submitting_form_creates_an_item_with_correct_fields(item_type):
    body = 'Hello, here is a new item'
    the_time = datetime(2015, 6, 27, 0, 0)
    (view, response) = make_request(
        AddEditItemView,
        'add-item',
        kwargs={'item_type': item_type['name']},
        request_type='post',
        post={
            'action': 'save',
            'timestamp': the_time,
            'next': '/',
            'id': 0,
            'body': body
        }
    )

    assert view.item['id'] > 0
    item = transport.items.get(view.item['id'])
    assert item['body'] == body
    assert timezone.make_naive(item['timestamp']) == the_time


@pytest.mark.django_db
def test_submitting_form_creates_an_item_with_a_category(item_type_taxonomy,
                                                         item_type):
    TermFactory(taxonomy=item_type_taxonomy, name='Ebola updates',
                long_name='What are the current updates on Ebola.')

    body = 'Hello, here is a new item'
    (view, response) = make_request(
        AddEditItemView,
        'add-item',
        kwargs={'item_type': item_type['name']},
        request_type='post',
        post={
            'action': 'save',
            'timestamp': datetime.now(),
            'next': '/',
            'id': 0,
            'category': 'Ebola updates',
            'body': body
        }
    )

    assert view.item['id'] > 0
    item = transport.items.get(view.item['id'])
    expected_term = {
        'taxonomy': item_type_taxonomy.slug,
        'name': 'Ebola updates',
        'long_name': 'What are the current updates on Ebola.'
    }

    assert expected_term in item['terms']


@pytest.mark.django_db
def test_item_can_be_deleted_with_post_request(item):
    taxonomy = TaxonomyFactory(name='Item Types', slug='item-types')
    TermFactory(taxonomy=taxonomy, name='concern', long_name='Concern')

    transport.items.add_terms(item['id'], 'item-types', 'concern')

    (view, response) = make_request(
        AddEditItemView,
        'edit-item',
        kwargs={'item_id': item['id']},
        request_type='post',
        post={
            'action': 'delete'
        }
    )

    with pytest.raises(TransportException) as excinfo:
        transport.items.get(item['id'])

    assert excinfo.value.message['status_code'] == 404

    assert_message(view.request,
                   messages.SUCCESS,
                   "Concern %s successfully deleted." % item['id'])


@pytest.mark.django_db
def test_item_can_be_updated(view, update_form):
    new_text = "What is the cause of Ebola?"
    update_form.cleaned_data['body'] = new_text

    view.form_valid(update_form)
    item = transport.items.get(view.item['id'])

    assert item['body'] == new_text


@pytest.mark.django_db
def test_new_item_cannot_have_duplicate_body_and_timestamp(view, new_form):
    other_item = transport.items.create(
        {
            'body': 'What is the cause of Ebola?',
        }
    )

    new_form.cleaned_data['body'] = other_item['body']
    new_form.cleaned_data['timestamp'] = other_item['timestamp']

    view.form_valid(new_form)

    assert_message(
        view.request,
        messages.ERROR,
        "This record could not be saved because the body and timestamp clashed with an existing record"
    )


@pytest.mark.django_db
def test_item_category_can_be_updated(view, update_form, item_type_taxonomy):
    TermFactory(taxonomy=item_type_taxonomy, name='Ebola updates')

    update_form.cleaned_data['category'] = 'Ebola updates',

    view.form_valid(update_form)
    item = transport.items.get(view.item['id'])

    terms = {t['taxonomy']: t['name'] for t in item['terms']}

    assert terms[item_type_taxonomy.slug] == 'Ebola updates'


@pytest.mark.django_db
def test_item_category_can_be_unset(view, update_form, item_type_taxonomy):
    TermFactory(taxonomy=item_type_taxonomy, name='Ebola origins')

    transport.items.add_terms(view.item['id'], item_type_taxonomy.slug,
                              'Ebola origins')

    update_form.cleaned_data['category'] = ''

    view.form_valid(update_form)
    item = transport.items.get(view.item['id'])

    terms = {t['taxonomy']: t['name'] for t in item['terms']}

    assert item_type_taxonomy.slug not in terms


@pytest.mark.django_db
def test_item_feedback_type_can_be_updated(view, update_form, taxonomies):  # noqa
    taxonomy = TaxonomyFactory(name='Item Types', slug='item-types')
    TermFactory(taxonomy=taxonomy, name='concern', long_name='Concern')
    TermFactory(taxonomy=taxonomy, name='rumour')

    transport.items.add_terms(view.item['id'], 'item-types', 'rumour')

    update_form.cleaned_data['feedback_type'] = 'concern',

    view.form_valid(update_form)
    assert_no_messages(view.request, messages.ERROR)

    item = transport.items.get(view.item['id'])

    terms = {t['taxonomy']: t['name'] for t in item['terms']}

    assert terms['item-types'] == 'concern'

    assert_message(view.request,
                   messages.SUCCESS,
                   "Concern %s successfully updated." % view.item['id'])


@pytest.mark.django_db
def test_item_feedback_type_can_be_unset(view, update_form, taxonomies):  # noqa
    taxonomy = TaxonomyFactory(name='Item Types', slug='item-types')
    TermFactory(taxonomy=taxonomy, name='concern')

    transport.items.add_terms(view.item['id'], 'item-types', 'concern')

    update_form.cleaned_data['feedback_type'] = ''

    view.form_valid(update_form)
    item = transport.items.get(view.item['id'])

    terms = {t['taxonomy']: t['name'] for t in item['terms']}

    assert 'item-types' not in terms

    # Message defaults to Question
    assert_message(view.request,
                   messages.SUCCESS,
                   "Question %s successfully updated." % view.item['id'])


@pytest.mark.django_db
def test_item_age_range_can_be_updated(view, update_form, taxonomies):  # noqa
    taxonomy = TaxonomyFactory(name='Age Ranges', slug='age-ranges')
    TermFactory(taxonomy=taxonomy, name='Age 11-14 yrs')
    TermFactory(taxonomy=taxonomy, name='Age 15-18 yrs')

    transport.items.add_terms(view.item['id'], 'age-ranges', 'Age 11-14 yrs')

    update_form.cleaned_data['age_range'] = 'Age 15-18 yrs',

    view.form_valid(update_form)
    assert_no_messages(view.request, messages.ERROR)

    item = transport.items.get(view.item['id'])

    terms = {t['taxonomy']: t['name'] for t in item['terms']}

    assert terms['age-ranges'] == 'Age 15-18 yrs'


@pytest.mark.django_db
def test_item_age_range_can_be_unset(view, update_form, item_type_taxonomy):
    taxonomy = TaxonomyFactory(name='Age Ranges', slug='age-ranges')
    TermFactory(taxonomy=taxonomy, name='Age 11-14 yrs')

    transport.items.add_terms(view.item['id'], 'age-ranges', 'Age 11-14 yrs')

    update_form.cleaned_data['age_range'] = ''

    view.form_valid(update_form)
    item = transport.items.get(view.item['id'])

    terms = {t['taxonomy']: t['name'] for t in item['terms']}

    assert 'age-ranges' not in terms


@pytest.mark.django_db
def test_item_category_not_required(view, update_form, item_type_taxonomy):
    TermFactory(taxonomy=item_type_taxonomy, name='Ebola origins')

    update_form.cleaned_data['category'] = ''

    view.form_valid(update_form)
    item = transport.items.get(view.item['id'])

    terms = {t['taxonomy']: t['name'] for t in item['terms']}

    assert item_type_taxonomy.slug not in terms


@pytest.mark.django_db
def test_item_update_logs_message_and_redirects(view, update_form, taxonomies):  # noqa
    item_type_taxonomy = Taxonomy.objects.get(name='Item Types')
    TermFactory(taxonomy=item_type_taxonomy, name='Ebola origins')

    view.item_type['long_name'] = 'Question'

    response = view.form_valid(update_form)
    assert response.url == update_form.cleaned_data['next']

    assert_message(view.request,
                   messages.SUCCESS,
                   "Question %s successfully updated." % view.item['id'])


@pytest.mark.django_db
def test_item_update_transport_exception_logs_message(view, update_form):
    # This could happen if someone else deletes the item when the
    # form is open
    transport.items.delete(view.item['id'])

    view.form_valid(update_form)

    assert_message(view.request,
                   messages.ERROR,
                   "Not found.")


@pytest.mark.django_db
def test_item_term_update_transport_exception_logs_message(view, update_form,
                                                           item_type_taxonomy):
    # This shouldn't be possible from the form but we may get other
    # TransportException errors
    update_form.cleaned_data['category'] = "A category that doesn't exist"
    view.form_valid(update_form)

    assert_message(view.request,
                   messages.ERROR,
                   "Term matching query does not exist.")


@pytest.mark.django_db
def test_item_term_delete_transport_exception_logs_message(view, update_form,
                                                           item_type_taxonomy):
    # This shouldn't be possible from the form but we may get other
    # TransportException errors
    update_form.cleaned_data['category'] = ''

    # Not sure if this is good practice
    old_category = ITEM_TYPE_CATEGORY['all']
    ITEM_TYPE_CATEGORY['all'] = 'unknown-slug'

    view.form_valid(update_form)

    ITEM_TYPE_CATEGORY['all'] = old_category

    assert_message(view.request,
                   messages.ERROR,
                   "Taxonomy with slug 'unknown-slug' does not exist.")


@pytest.mark.django_db
def test_item_can_be_deleted(view):
    view._delete_item()

    assert_message(view.request,
                   messages.SUCCESS,
                   "Question %s successfully deleted." % view.item['id'])

    with pytest.raises(TransportException) as excinfo:
        transport.items.get(view.item['id'])

    assert excinfo.value.message['status_code'] == 404


@pytest.mark.django_db
def test_free_tags_created_on_item_update(view, update_form, taxonomies):  # noqa
    # Deliberate spaces to be stripped
    update_form.cleaned_data['tags'] = 'Monrovia , Important ,age 35-40'

    view.form_valid(update_form)
    assert_no_messages(view.request, messages.ERROR)

    item = transport.items.get(view.item['id'])

    terms = [t['name'] for t in item['terms']]
    assert 'Monrovia' in terms
    assert 'Important' in terms
    assert 'age 35-40' in terms

    taxonomies = [t['taxonomy'] for t in item['terms']]
    assert 'tags' in taxonomies


@pytest.mark.django_db
def test_existing_tag_deleted_on_item_update(view, update_form, taxonomies):  # noqa
    transport.items.add_terms(view.item['id'], 'tags', ['age 35-40'])

    update_form.cleaned_data['tags'] = 'Monrovia'

    view.form_valid(update_form)
    assert_no_messages(view.request, messages.ERROR)

    item = transport.items.get(view.item['id'])

    terms = [t['name'] for t in item['terms']]
    assert 'Monrovia' in terms
    assert 'age 35-40' not in terms


@pytest.mark.django_db
def test_free_tags_created_for_new_item(add_view, new_form):
    new_form.cleaned_data['tags'] = 'Monrovia,Important,age 35-40'
    new_form.cleaned_data['body'] = 'Message'
    new_form.cleaned_data['timestamp'] = datetime.now()

    add_view.form_valid(new_form)
    assert_no_messages(add_view.request, messages.ERROR)

    item = transport.items.get(add_view.item['id'])

    terms = [t['name'] for t in item['terms']]
    assert 'Monrovia' in terms
    assert 'Important' in terms
    assert 'age 35-40' in terms

    taxonomy_list = [t['taxonomy'] for t in item['terms']]
    assert 'tags' in taxonomy_list


@pytest.mark.django_db
def test_data_origin_created_for_new_item(add_view, new_form):
    new_form.cleaned_data['body'] = 'Message'
    new_form.cleaned_data['timestamp'] = datetime.now()

    add_view.form_valid(new_form)
    assert_no_messages(add_view.request, messages.ERROR)

    item = transport.items.get(add_view.item['id'])

    terms = [t['name'] for t in item['terms']]
    assert 'Form Entry' in terms

    taxonomy_list = [t['taxonomy'] for t in item['terms']]
    assert 'data-origins' in taxonomy_list


@pytest.mark.django_db
def test_feedback_type_for_new_item(add_view, new_form):
    taxonomy = TaxonomyFactory(name='Item Types', slug='item-types')
    TermFactory(taxonomy=taxonomy, name='rumour', long_name='Rumour')

    new_form.cleaned_data['feedback_type'] = 'rumour'
    new_form.cleaned_data['body'] = 'Message'
    new_form.cleaned_data['timestamp'] = datetime.now()

    add_view.form_valid(new_form)
    assert_no_messages(add_view.request, messages.ERROR)

    item = transport.items.get(add_view.item['id'])

    terms = [t for t in item['terms'] if t['taxonomy'] == 'item-types']

    assert len(terms) == 1

    assert terms[0]['name'] == 'rumour'
    assert_message(add_view.request,
                   messages.SUCCESS,
                   "Rumour %s successfully created." % add_view.item['id'])


@pytest.mark.django_db
def test_form_initial_values_include_tags(generic_item):
    with patch('hid.views.item.transport.items.get') as get_item:
        generic_item['terms'] = [
            {
                'taxonomy': 'tags',
                'name': 'Monrovia',
                'long_name': 'Monrovia',
            },
            {
                'taxonomy': 'tags',
                'name': 'age 35-40',
                'long_name': 'Age 35-40',
            },
            {
                'taxonomy': 'tags',
                'name': 'interesting',
                'long_name': 'Interesting',
            },
        ]

        get_item.return_value = generic_item

        (view, response) = make_request(
            AddEditItemView,
            'edit-item',
            kwargs={'item_id': 103}
        )

    initial = view.get_initial()
    assert initial['tags'] == 'Monrovia,age 35-40,interesting'


@pytest.mark.django_db
def test_form_initial_values_include_feedback_type(generic_item):
    with patch('hid.views.item.transport.items.get') as get_item:
        generic_item['terms'] = [
            {
                'taxonomy': 'item-types',
                'name': 'concern',
                'long_name': 'Concern',
            },
        ]

        get_item.return_value = generic_item

        (view, response) = make_request(
            AddEditItemView,
            'edit-item',
            kwargs={'item_id': 103}
        )

        initial = view.get_initial()
        assert initial['feedback_type'] == 'concern'


@pytest.mark.django_db
def test_feedback_disabled_if_user_does_not_have_permission(generic_item):
    with patch('hid.views.item.transport.items.get') as get_item:
        get_item.return_value = generic_item

        view = get_view_for_request(AddEditItemView, 'edit-item',
                                    kwargs={'item_id': 1})

        user = Mock()
        user.has_perm.return_value = False

        view.request.user = user

        response = view.get(view.request, *view.args, **view.kwargs)
        user.has_perm.assert_called_with('data_layer.can_change_message_body')

        form = response.context_data['form']

        assert form.fields['body'].disabled is True


@pytest.mark.django_db
def test_feedback_enabled_if_user_has_permission(generic_item):
    with patch('hid.views.item.transport.items.get') as get_item:
        get_item.return_value = generic_item

        view = get_view_for_request(AddEditItemView, 'edit-item',
                                    kwargs={'item_id': 1})

        user = Mock()
        user.has_perm.return_value = True

        view.request.user = user

        response = view.get(view.request, *view.args, **view.kwargs)
        user.has_perm.assert_called_with('data_layer.can_change_message_body')

        form = response.context_data['form']

        assert form.fields['body'].disabled is False
