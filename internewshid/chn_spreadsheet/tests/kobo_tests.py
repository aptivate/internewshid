import datetime
from os import path

import pytest

import transport
from importer_tests import importer

TEST_BASE_DIR = path.abspath(path.dirname(__file__))
TEST_DIR = path.join(TEST_BASE_DIR, 'test_files')


@pytest.mark.django_db
def test_kobo_items_imported(importer):
    assert len(transport.items.list()) == 0

    file_path = path.join(TEST_DIR, 'sample_kobo.xlsx')
    f = open(file_path, 'rb')

    num_saved = importer.store_spreadsheet('kobo', f)
    assert num_saved > 0

    items = transport.items.list()

    assert len(items) == num_saved

    assert items[0]['body'] == 'the community members want more food.'
    assert items[0]['translation'] == ''
    assert isinstance(items[0]['timestamp'], datetime.datetime)

    tags = []
    for term in items[0]['terms']:
        if term['taxonomy'] == 'tags':
            tags.append(term['name'])

    assert len(tags) > 0
    assert all(tag in tags for tag in (
        'female',
        'Camp 4',
    ))
