from __future__ import unicode_literals, absolute_import
import pytest

from django.core.urlresolvers import reverse
from rest_framework.test import APIRequestFactory
from rest_framework import status

from ..views import TermCountViewSet

from .categorize_items_tests import categorize_item
from .item_create_view_tests import create_item
from .taxonomy_and_term_create_tests import (
    create_category,
    add_term,
)


def get_term_count(taxonomy):
    url = reverse('term-list', kwargs={"taxonomy": taxonomy['slug']})
    request = APIRequestFactory().get(url)
    view = TermCountViewSet.as_view({'get': 'list'})

    response = view(request)
    assert status.is_success(response.status_code), response.data

    return response



@pytest.mark.django_db
def test_term_count_returns_dict_keyed_on_short_name():
    origin1 = create_item(body="What was the caused of ebola outbreak in liberia?").data
    origin2 = create_item(body="Is Ebola a man made sickness").data
    origin3 = create_item(body="What brought about ebola in liberia").data

    victims1 = create_item(body="How many person died of Ebola in Liberia?").data

    updates1 = create_item(body="When will Liberia be free from Ebola?").data
    updates2 = create_item(body="Is ebola still here or not?").data

    questions = create_category("Test Ebola Questions").data

    origins = add_term(taxonomy=questions['slug'], name="Test Origins").data
    victims = add_term(taxonomy=questions['slug'], name="Test Victims").data
    updates = add_term(taxonomy=questions['slug'], name="Test Updates").data

    regions = create_category("Regions").data
    monrovia = add_term(taxonomy=regions['slug'], name="Monrovia").data

    categorize_item(origin1, origins)
    categorize_item(origin2, origins)
    categorize_item(origin3, origins)

    categorize_item(victims1, victims)

    categorize_item(updates1, updates)
    categorize_item(updates2, updates)

    categorize_item(origin1, monrovia)
    categorize_item(updates1, monrovia)

    term_count = get_term_count(questions).data

    # {
    #   'Vaccine' :
    #     {
    #       'long_name': 'What is the status of the Ebola vaccine',
    #       'count': 27,
    #     },
    #    'Symptoms':
    #     {
    #       'long_name': 'What are the symptoms of Ebola?',
    #       'count': 1
    #     },
    #     ...
    # }

    assert origins['name'] in term_count
    assert victims.name in term_count
    assert updates.name in term_count

    assert monrovia.name not in term_count
