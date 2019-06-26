from __future__ import absolute_import, unicode_literals

from datetime import timedelta

from django.utils import timezone

import pytest

import transport
from taxonomies.tests.factories import TaxonomyFactory, TermFactory

from ..exceptions import TransportException


def time_now():
    return timezone.now().replace(
        microsecond=0  # MySQL discards microseconds
    )


def item_data(**kwargs):
    item = kwargs
    item['body'] = "What is the cuse of ebola?"
    return transport.items.create(item)


@pytest.fixture
def questions_category():
    # TODO: Replace with transport call when we have one
    return TaxonomyFactory(name="Test Ebola Questions")


@pytest.fixture
def questions_term(questions_category):
    # TODO: Replace with transport call when we have one
    return TermFactory(taxonomy=questions_category)


@pytest.mark.django_db
def test_term_itemcount_returns_terms_and_counts(questions_category,
                                                 questions_term):

    # This is tested more comprehensively in the API tests
    transport.items.add_terms(item_data()['id'],
                              questions_category.slug,
                              questions_term.name)

    terms = transport.taxonomies.term_itemcount(slug=questions_category.slug)
    counts = {term['name']: term['count'] for term in terms}

    assert counts[questions_term.name] == 1


@pytest.mark.django_db
def test_itemcount_fails_if_taxonomy_does_not_exist():
    with pytest.raises(TransportException) as excinfo:
        transport.taxonomies.term_itemcount(
            slug='a-taxonomy-that-does-not-exist')

    error = excinfo.value.message

    assert error['status_code'] == 400
    assert error['detail'] == "Taxonomy with slug 'a-taxonomy-that-does-not-exist' does not exist."


@pytest.mark.django_db
def test_term_itemcount_returns_terms_and_counts_for_range(
        questions_category,
        questions_term):

    now = time_now()

    items = [item_data(timestamp=now - timedelta(days=d)) for d in range(0, 9)]

    for item in items:
        transport.items.add_terms(item['id'],
                                  questions_category.slug,
                                  questions_term.name)

    # 9 8 7 6 5 4 3 2 1 0
    # n y y y y y y y n n
    start_time = now - timedelta(days=8)
    end_time = now - timedelta(days=2)

    [term] = transport.taxonomies.term_itemcount(
        slug=questions_category.slug,
        start_time=start_time,
        end_time=end_time)

    assert term['count'] == 7


@pytest.mark.django_db
def test_term_itemcount_returns_zero_term_counts_for_range(
        questions_category,
        questions_term):

    now = time_now()
    one_day_ago = now - timedelta(days=1)
    one_week_ago = now - timedelta(weeks=1)
    eight_days_ago = now - timedelta(days=8)

    item_too_recent = item_data(timestamp=now)
    item_too_old = item_data(timestamp=eight_days_ago)

    transport.items.add_terms(item_too_recent['id'],
                              questions_category.slug,
                              questions_term.name)
    transport.items.add_terms(item_too_old['id'],
                              questions_category.slug,
                              questions_term.name)

    [term] = transport.taxonomies.term_itemcount(
        slug=questions_category.slug,
        start_time=one_week_ago,
        end_time=one_day_ago)

    assert term['count'] == 0
