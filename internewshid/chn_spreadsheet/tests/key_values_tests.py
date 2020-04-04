import datetime
from os import path

from django.core.management import call_command

import pytest

import transport
from chn_spreadsheet.tests.conftest import taxonomies  # noqa

TEST_BASE_DIR = path.abspath(path.dirname(__file__))
TEST_DIR = path.join(TEST_BASE_DIR, 'test_files')


@pytest.fixture
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command('loaddata', 'spreadsheet-profiles.json')


@pytest.mark.django_db  # noqa
def test_kobo_keyvalue_imported(importer, django_db_setup, taxonomies):  # noqa
    assert len(transport.items.list_items()['results']) == 0

    file_path = path.join(TEST_DIR, 'sample_kobo_keyValues.xlsx')
    (num_saved, _) = importer.store_spreadsheet('kobo', open(file_path, 'rb'))

    assert num_saved > 0

    items = transport.items.list_items()['results']
    assert len(items) == num_saved

    # default ordering is by timestamp desc
    assert items[4]['body'] == 'the community members want more food.'
    assert items[4]['translation'] == ''
    assert items[4]['location'] == 'Camp 4'
    assert items[4]['language'] == 'English'
    assert items[4]['risk'] == 'low risk'
    assert items[4]['values']['KV1'] == 'one'
    assert items[3]['values']['KV1'] == '2020-12-12 00:00:00'
    assert items[0]['values']['KV1'] == '123'
    assert isinstance(items[2]['timestamp'], datetime.datetime)
