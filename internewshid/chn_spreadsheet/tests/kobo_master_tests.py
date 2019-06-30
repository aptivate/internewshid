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
        call_command('loaddata', 'bangladesh-refugee-crisis.json')


@pytest.mark.django_db  # noqa
def test_kobo_master_items_imported(importer, django_db_setup):
    assert len(transport.items.list()) == 0

    file_path = path.join(TEST_DIR, 'sample_kobo_master.xlsx')
    (num_saved, _) = importer.store_spreadsheet('kobo_master', open(file_path, 'rb'))

    assert num_saved > 0

    items = transport.items.list()

    assert len(items) == num_saved

    assert items[0]['body'] == 'sample feedback'
    assert items[0]['translation'] == 'sample translation'
    assert items[0]['gender'] == 'male'
    assert items[0]['age'] == '41'
    assert items[0]['location'] == 'Camp 1W'
    assert items[0]['enumerator'] == 'osman'
    assert items[0]['source'] == 'sample source'
    assert isinstance(items[0]['timestamp'], datetime.datetime)

    tags = []
    for item in items:
        for term in item['terms']:
            if term['taxonomy'] == 'tags':
                assert term['name'] != 'None'
                tags.append(term['name'])

    assert len(tags) > 0
    assert all(tag in tags for tag in (
        'sample tag',
    ))


@pytest.mark.django_db  # noqa
def test_items_cannot_be_imported_twice(importer, django_db_setup):
    file_path = path.join(TEST_DIR, 'master_kobo_single_item.xlsx')
    (num_saved, num_skipped) = importer.store_spreadsheet('kobo_master', open(file_path, 'rb'))

    assert num_saved == 1
    assert num_skipped == 0

    (num_saved, num_skipped) = importer.store_spreadsheet('kobo_master', open(file_path, 'rb'))

    assert num_saved == 0
    assert num_skipped == 1
