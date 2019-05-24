import datetime
from os import path

from django.core.management import call_command

import pytest

import transport
from data_layer.models import Item
from importer_tests import importer  # noqa

TEST_BASE_DIR = path.abspath(path.dirname(__file__))
TEST_DIR = path.join(TEST_BASE_DIR, 'test_files')


@pytest.fixture
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command('loaddata', 'bangladesh-refugee-crisis.json')


@pytest.mark.django_db  # noqa
def test_kobo_items_imported(importer, django_db_setup):
    assert len(transport.items.list()) == 0

    file_path = path.join(TEST_DIR, 'sample_kobo.xlsx')
    (num_saved, _) = importer.store_spreadsheet('kobo', open(file_path, 'rb'))

    assert num_saved > 0

    items = transport.items.list()

    assert len(items) == num_saved

    assert items[0]['body'] == 'the community members want more food.'
    assert items[0]['translation'] == ''
    assert items[0]['location'] == 'Camp 4'
    assert isinstance(items[0]['timestamp'], datetime.datetime)


@pytest.mark.django_db  # noqa
def test_kobo_empty_body_is_allowed(importer):
    file_path = path.join(TEST_DIR, 'sample_kobo.xlsx')
    importer.store_spreadsheet('kobo', open(file_path, 'rb'))
    items = transport.items.list()

    with_empty_body_item = items[1]

    assert with_empty_body_item['body'] == ''

    assert Item.objects.count() == 3
