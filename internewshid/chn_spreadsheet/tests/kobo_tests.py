import datetime
from os import path

from django.core.management import call_command

import pytest

import transport
from chn_spreadsheet.tests.conftest import taxonomies  # noqa
from data_layer.models import Item

TEST_BASE_DIR = path.abspath(path.dirname(__file__))
TEST_DIR = path.join(TEST_BASE_DIR, 'test_files')


@pytest.fixture
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command('loaddata', 'spreadsheet-profiles.json')


@pytest.mark.django_db  # noqa
def test_kobo_items_imported(importer, django_db_setup, taxonomies):  # noqa
    assert len(transport.items.list_items()['results']) == 0

    file_path = path.join(TEST_DIR, 'sample_kobo.xlsx')
    (num_saved, _) = importer.store_spreadsheet('kobo', open(file_path, 'rb'))

    assert num_saved > 0

    items = transport.items.list_items()['results']

    assert len(items) == num_saved

    # default ordering is by timestamp desc
    assert items[2]['body'] == 'the community members want more food.'
    assert items[2]['translation'] == ''
    assert items[2]['location'] == 'Camp 4'
    assert items[2]['language'] == 'English'
    assert isinstance(items[2]['timestamp'], datetime.datetime)


@pytest.mark.django_db  # noqa
def test_kobo_empty_body_is_allowed(importer, taxonomies):  # noqa
    file_path = path.join(TEST_DIR, 'sample_kobo.xlsx')
    importer.store_spreadsheet('kobo', open(file_path, 'rb'))
    items = transport.items.list_items(external_id_pattern='e057')['results']

    assert len(items) == 1
    assert items[0]['body'] == ''

    assert Item.objects.count() == 3
