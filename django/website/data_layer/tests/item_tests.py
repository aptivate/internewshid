import pytest

from django.utils import timezone

from factories import ItemFactory
from ..models import Item
from taxonomies.tests.factories import TermFactory

import datetime
from mock import patch, MagicMock


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
def test_last_modified_date_updates_on_category_item_add(
        item, mock_time_now):
    with patch('django.utils.timezone.now', new=mock_time_now):
        orig_last_modified = last_modified(item)
        term = TermFactory()
        term.items.add(item)

        assert num_updates(orig_last_modified, last_modified(item)) == 1
