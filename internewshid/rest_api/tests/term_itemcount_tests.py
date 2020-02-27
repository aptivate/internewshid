from datetime import timedelta

from django.utils import timezone

import pytest
from rest_framework import status
from rest_framework.test import APIRequestFactory

from ..views import TaxonomyViewSet
from .categorize_items_tests import categorize_item
from .item_create_view_tests import create_item
from .taxonomy_and_term_create_tests import add_term, create_taxonomy


def get_term_itemcount(taxonomy_slug, get_params=None):
    response = get_term_itemcount_response(taxonomy_slug, get_params)
    assert status.is_success(response.status_code), response.data

    return response


def get_term_itemcount_response(taxonomy_slug, get_params=None):
    request = APIRequestFactory().get("", data=get_params)
    view = TaxonomyViewSet.as_view(actions={'get': 'itemcount'})

    return view(request, slug=taxonomy_slug)


@pytest.fixture
def questions_category_slug():
    return create_taxonomy(name="Test Ebola Questions").data['slug']


@pytest.fixture
def regions_category():
    return create_taxonomy(name="Regions").data


@pytest.mark.django_db
def test_term_itemcount_returns_counts_for_terms_in_taxonomy(
        questions_category_slug, regions_category):
    origin1 = create_item(body="What was the caused of ebola outbreak in liberia?").data
    origin2 = create_item(body="Is Ebola a man made sickness").data
    origin3 = create_item(body="What brought about ebola in liberia").data

    victims1 = create_item(body="How many person died of Ebola in Liberia?").data

    updates1 = create_item(body="When will Liberia be free from Ebola?").data
    updates2 = create_item(body="Is ebola still here or not?").data

    origins = add_term(taxonomy=questions_category_slug, name="Test Origins").data
    victims = add_term(taxonomy=questions_category_slug, name="Test Victims").data
    updates = add_term(taxonomy=questions_category_slug, name="Test Updates").data

    monrovia = add_term(taxonomy=regions_category['slug'], name="Monrovia").data

    categorize_item(origin1, origins)
    categorize_item(origin2, origins)
    categorize_item(origin3, origins)

    categorize_item(victims1, victims)

    categorize_item(updates1, updates)
    categorize_item(updates2, updates)

    categorize_item(origin1, monrovia)
    categorize_item(updates1, monrovia)

    terms = get_term_itemcount(questions_category_slug).data

    counts = {term['name']: term['count'] for term in terms}

    assert counts[origins['name']] == 3
    assert counts[victims['name']] == 1
    assert counts[updates['name']] == 2


@pytest.mark.django_db
def test_term_itemcount_contains_taxonomy_term_name(questions_category_slug):
    origin1 = create_item(body="What was the caused of ebola outbreak in liberia?").data
    origins = add_term(taxonomy=questions_category_slug, name="Test Origins").data
    categorize_item(origin1, origins)

    terms = get_term_itemcount(questions_category_slug).data
    [name] = [term['name'] for term in terms]

    assert origins['name'] == name


@pytest.mark.django_db
def test_term_itemcount_does_not_contain_term_for_other_taxonomy(
        questions_category_slug, regions_category):
    origin1 = create_item(body="What was the caused of ebola outbreak in liberia?").data
    origins = add_term(taxonomy=questions_category_slug, name="Test Origins").data
    monrovia = add_term(taxonomy=regions_category['slug'], name="Monrovia").data

    categorize_item(origin1, origins)
    categorize_item(origin1, monrovia)

    terms = get_term_itemcount(questions_category_slug).data
    names = [term['name'] for term in terms]

    assert monrovia['name'] not in names


@pytest.mark.django_db
def test_term_itemcount_contains_taxonomy_term_long_name(
        questions_category_slug):
    origin1 = create_item(body="What was the caused of ebola outbreak in liberia?").data
    origins = add_term(taxonomy=questions_category_slug,
                       name="Test Origins").data
    categorize_item(origin1, origins)

    terms = get_term_itemcount(questions_category_slug).data
    [long_name] = [term['long_name'] for term in terms]

    assert origins['long_name'] == long_name


@pytest.mark.django_db
def test_items_in_date_range_returned(questions_category_slug):
    now = timezone.now().replace(
        microsecond=0  # MySQL discards microseconds
    )

    one_day_ago = now - timedelta(days=1)
    one_week_ago = now - timedelta(weeks=1)
    eight_days_ago = now - timedelta(days=8)

    item_too_recent = create_item(
        body="Where did ebola came from?",
        timestamp=now
    ).data
    item_in_range_1 = create_item(
        body="What was the caused of ebola outbreak in liberia?",
        timestamp=one_day_ago
    ).data
    item_in_range_2 = create_item(
        body="Is Ebola a man made sickness",
        timestamp=one_week_ago
    ).data
    item_too_old = create_item(
        body="What brought about ebola in liberia",
        timestamp=eight_days_ago
    ).data

    origins = add_term(taxonomy=questions_category_slug, name="Test Origins").data

    categorize_item(item_in_range_1, origins)
    categorize_item(item_in_range_2, origins)
    categorize_item(item_too_old, origins)
    categorize_item(item_too_recent, origins)

    get_params = {
        'start_time': one_week_ago,
        'end_time': one_day_ago}

    [term] = get_term_itemcount(questions_category_slug, get_params).data

    assert term['count'] == 2


@pytest.mark.django_db
def test_error_for_non_existent_taxonomy():
    response = get_term_itemcount_response('a-taxonomy-that-does-not-exist')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['detail'] == "Taxonomy with slug 'a-taxonomy-that-does-not-exist' does not exist."
