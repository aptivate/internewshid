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
def now_iter(start):
    t = start
    while True:
        t += datetime.timedelta(hours=1)
        yield t


@pytest.mark.django_db
def test_last_modified_date_updates_on_body_change():
    item = ItemFactory()
    magic_mock = MagicMock(wraps=timezone.now,
                           side_effect=now_iter(timezone.now()))

    with patch('django.utils.timezone.now', new=magic_mock):
        orig_last_modified = last_modified(item)
        item.body = 'replacement text'
        item.save()

        assert orig_last_modified < last_modified(item)


@pytest.mark.django_db
def test_last_modified_date_updates_on_category_change():
    item = ItemFactory()
    magic_mock = MagicMock(wraps=timezone.now,
                           side_effect=now_iter(timezone.now()))

    with patch('django.utils.timezone.now', new=magic_mock):
        orig_last_modified = last_modified(item)
        term = TermFactory()
        item.terms.add(term)

        assert orig_last_modified < last_modified(item)
