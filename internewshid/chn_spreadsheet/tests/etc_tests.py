import datetime
from os import path

from django.core.management import call_command

import pytest

import transport

TEST_BASE_DIR = path.abspath(path.dirname(__file__))
TEST_DIR = path.join(TEST_BASE_DIR, 'test_files')


@pytest.fixture
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command('loaddata', 'spreadsheet-profiles.json')


@pytest.mark.django_db  # noqa
def test_etc_items_imported(importer, django_db_setup):
    assert len(transport.items.list_items()['results']) == 0

    file_path = path.join(TEST_DIR, 'sample_etc.xlsx')
    (num_saved, _) = importer.store_spreadsheet('etc', open(file_path, 'rb'))

    assert num_saved > 0

    items = transport.items.list_items()['results']

    assert len(items) == num_saved

    assert items[0]['location'] == 'Camp 1E'
    assert isinstance(items[0]['timestamp'], datetime.datetime)

    tags = []
    for term in items[0]['terms']:
        if term['taxonomy'] == 'tags':
            tags.append(term['name'])

    assert len(tags) > 0
    assert all(tag in tags for tag in (
        'Male',
    ))
