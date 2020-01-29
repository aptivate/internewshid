import datetime

from django.utils import timezone

import pytest
from mock import MagicMock, patch

from .factories import ItemFactory
from taxonomies.exceptions import TermException
from taxonomies.tests.factories import TaxonomyFactory, TermFactory

from ..models import Item


def last_modified(item):
    return Item.objects.get(id=item.id).last_modified


# Ensure value of "now" always increases by amount sufficient
# to show up as a change, even if db resolution for datetime
# is one second.
def time_granularity():
    return datetime.timedelta(hours=1)


def now_iter(start):
    t = start
    while True:
        t += time_granularity()
        yield t


def num_updates(old_time, new_time):
    elapsed_time = new_time - old_time

    return elapsed_time.seconds / time_granularity().seconds


@pytest.fixture
def item():
    return ItemFactory()


@pytest.fixture
def mock_time_now():
    return MagicMock(wraps=timezone.now,
                     side_effect=now_iter(timezone.now()))


@pytest.fixture
def multiple_taxonomy():
    return TaxonomyFactory(multiplicity='multiple')


@pytest.fixture
def optional_taxonomy1():
    return TaxonomyFactory()


@pytest.fixture
def optional_taxonomy2():
    return TaxonomyFactory()


@pytest.fixture
def optional_term1(optional_taxonomy1):
    return TermFactory(taxonomy=optional_taxonomy1)


@pytest.fixture
def optional_term2(optional_taxonomy1):
    return TermFactory(taxonomy=optional_taxonomy1)


@pytest.fixture
def multiple_term1(multiple_taxonomy):
    return TermFactory(taxonomy=multiple_taxonomy)


@pytest.fixture
def multiple_term2(multiple_taxonomy):
    return TermFactory(taxonomy=multiple_taxonomy)


@pytest.mark.django_db
def test_last_modified_date_updates_on_body_change(item, mock_time_now):
    with patch('django.utils.timezone.now', new=mock_time_now):
        orig_last_modified = last_modified(item)
        item.body = 'replacement text'
        item.save()

        assert num_updates(orig_last_modified, last_modified(item)) == 1


@pytest.mark.django_db
def test_last_modified_date_updates_on_item_category_add(
        item, mock_time_now):
    with patch('django.utils.timezone.now', new=mock_time_now):
        orig_last_modified = last_modified(item)
        term = TermFactory()
        item.terms.add(term)

        assert num_updates(orig_last_modified, last_modified(item)) == 1


@pytest.mark.django_db
def test_last_modified_date_updates_on_item_category_delete(
        item, mock_time_now):
    with patch('django.utils.timezone.now', new=mock_time_now):
        term = TermFactory()
        item.terms.add(term)
        orig_last_modified = last_modified(item)
        item.terms.remove(term)

        assert num_updates(orig_last_modified, last_modified(item)) == 1


@pytest.mark.django_db
def test_last_modified_date_updates_on_category_item_add(
        item, mock_time_now):
    with patch('django.utils.timezone.now', new=mock_time_now):
        orig_last_modified = last_modified(item)
        term = TermFactory()
        term.items.add(item)

        assert num_updates(orig_last_modified, last_modified(item)) == 1


@pytest.mark.django_db
def test_last_modified_date_updates_on_category_item_delete(
        item, mock_time_now):
    with patch('django.utils.timezone.now', new=mock_time_now):
        term = TermFactory()
        term.items.add(item)
        orig_last_modified = last_modified(item)
        term.items.remove(item)

        assert num_updates(orig_last_modified, last_modified(item)) == 1


@pytest.mark.django_db
def test_last_modified_date_on_other_item_not_updated(
        item, mock_time_now):
    with patch('django.utils.timezone.now', new=mock_time_now):
        term = TermFactory()
        term.items.add(item)

        other_item = ItemFactory()
        term.items.add(other_item)

        orig_last_modified = last_modified(other_item)
        term.items.remove(item)

        assert num_updates(orig_last_modified, last_modified(other_item)) == 0


@pytest.mark.django_db
def test_apply_terms_replaces_term_for_categories(item,
                                                  optional_term1,
                                                  optional_term2):
    item.apply_terms(optional_term1)
    assert list(item.terms.all()) == [optional_term1]

    item.apply_terms(optional_term2)
    assert list(item.terms.all()) == [optional_term2]


@pytest.mark.django_db
def test_apply_terms_adds_term_for_tags(item,
                                        multiple_term1,
                                        multiple_term2):
    item.apply_terms(multiple_term1)
    assert list(item.terms.all()) == [multiple_term1]

    item.apply_terms(multiple_term2)
    assert multiple_term1 in item.terms.all()
    assert multiple_term2 in item.terms.all()


@pytest.mark.django_db
def test_apply_terms_adds_multiple_terms(item,
                                         multiple_term1,
                                         multiple_term2):

    item.apply_terms((multiple_term1, multiple_term2))
    assert multiple_term1 in item.terms.all()
    assert multiple_term2 in item.terms.all()


@pytest.mark.django_db
def test_applying_multiple_terms_raises_exception_if_not_multiple(
        item, optional_term1, optional_term2):

    with pytest.raises(TermException) as excinfo:
        item.apply_terms((optional_term1, optional_term2))

    expected_message = "Taxonomy '%s' does not support multiple terms" % (
        optional_term1.taxonomy)
    assert str(excinfo.value) == expected_message


@pytest.mark.django_db
def test_applied_terms_must_be_from_same_taxonomy(item,
                                                  optional_taxonomy1,
                                                  optional_taxonomy2):
    term1 = TermFactory(taxonomy=optional_taxonomy1)
    term2 = TermFactory(taxonomy=optional_taxonomy2)

    term3 = TermFactory(taxonomy=optional_taxonomy1)

    with pytest.raises(TermException) as excinfo:
        item.apply_terms((term1, term2, term3))

    expected_message = "Terms cannot be applied from different taxonomies"
    assert str(excinfo.value) == expected_message
