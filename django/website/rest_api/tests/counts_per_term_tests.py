from __future__ import unicode_literals, absolute_import
import pytest

from django.core.urlresolvers import reverse
from rest_framework.test import APIRequestFactory
from rest_framework import status

from ..views import TaxonomyViewSet

from .categorize_items_tests import categorize_item
from .item_create_view_tests import create_item
from .taxonomy_and_term_create_tests import (
    create_category,
    add_term,
)


def get_term_itemcount(taxonomy):
    url = reverse('taxonomy-itemcount', kwargs={'slug': taxonomy['slug']})
    request = APIRequestFactory().get(url)
    view = TaxonomyViewSet.as_view(actions={'get': 'itemcount'})

    response = view(request, slug=taxonomy['slug'])
    assert status.is_success(response.status_code), response.data

    return response


@pytest.fixture
def questions_category():
    return create_category("Test Ebola Questions").data


@pytest.fixture
def regions_category():
    return create_category("Regions").data


@pytest.mark.django_db
def test_term_itemcount_returns_counts_for_terms_in_taxonomy(
        questions_category, regions_category):
    origin1 = create_item(body="What was the caused of ebola outbreak in liberia?").data
    origin2 = create_item(body="Is Ebola a man made sickness").data
    origin3 = create_item(body="What brought about ebola in liberia").data

    victims1 = create_item(body="How many person died of Ebola in Liberia?").data

    updates1 = create_item(body="When will Liberia be free from Ebola?").data
    updates2 = create_item(body="Is ebola still here or not?").data

    origins = add_term(taxonomy=questions_category['slug'], name="Test Origins").data
    victims = add_term(taxonomy=questions_category['slug'], name="Test Victims").data
    updates = add_term(taxonomy=questions_category['slug'], name="Test Updates").data

    monrovia = add_term(taxonomy=regions_category['slug'], name="Monrovia").data

    categorize_item(origin1, origins)
    categorize_item(origin2, origins)
    categorize_item(origin3, origins)

    categorize_item(victims1, victims)

    categorize_item(updates1, updates)
    categorize_item(updates2, updates)

    categorize_item(origin1, monrovia)
    categorize_item(updates1, monrovia)

    terms = get_term_itemcount(questions_category).data

    counts = {term['name']: term['count'] for term in terms}

    assert counts[origins['name']] == 3
    assert counts[victims['name']] == 1
    assert counts[updates['name']] == 2


@pytest.mark.django_db
def test_term_itemcount_contains_taxonomy_term_name(questions_category):
    origin1 = create_item(body="What was the caused of ebola outbreak in liberia?").data
    origins = add_term(taxonomy=questions_category['slug'], name="Test Origins").data
    categorize_item(origin1, origins)

    terms = get_term_itemcount(questions_category).data
    [name] = [term['name'] for term in terms]

    assert origins['name'] == name


@pytest.mark.django_db
def test_term_itemcount_does_not_contain_term_for_other_taxonomy(
        questions_category, regions_category):
    origin1 = create_item(body="What was the caused of ebola outbreak in liberia?").data
    origins = add_term(taxonomy=questions_category['slug'], name="Test Origins").data
    monrovia = add_term(taxonomy=regions_category['slug'], name="Monrovia").data

    categorize_item(origin1, origins)
    categorize_item(origin1, monrovia)

    terms = get_term_itemcount(questions_category).data
    names = [term['name'] for term in terms]

    assert monrovia['name'] not in names


@pytest.mark.django_db
def test_term_itemcount_contains_taxonomy_term_long_name(questions_category):
    origin1 = create_item(body="What was the caused of ebola outbreak in liberia?").data
    origins = add_term(taxonomy=questions_category['slug'], name="Test Origins").data
    categorize_item(origin1, origins)

    terms = get_term_itemcount(questions_category).data
    [long_name] = [term['long_name'] for term in terms]

    assert origins['long_name'] == long_name
