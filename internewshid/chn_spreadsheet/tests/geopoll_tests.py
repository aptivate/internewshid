import datetime
from os import path

import pytest
import pytz

import transport
from importer_tests import importer

TEST_BASE_DIR = path.abspath(path.dirname(__file__))
TEST_DIR = path.join(TEST_BASE_DIR, 'test_files')


@pytest.mark.django_db
def test_items_imported(importer):
    assert len(transport.items.list()) == 0

    file_path = path.join(TEST_DIR, 'sample_geopoll.xlsx')
    f = open(file_path, 'rb')

    num_saved = importer.store_spreadsheet('geopoll', f)
    assert num_saved > 0

    items = transport.items.list()
    assert len(items) == num_saved

    assert items[0]['body'] == "What  is  the  cuse  of  ebola?"
    assert items[0]['timestamp'] == pytz.utc.localize(
        datetime.datetime(2015, 5, 1))

    item_types = transport.taxonomies.term_itemcount(
        slug='item-types')

    counts_per_item = {t['name']: t['count'] for t in item_types}

    assert counts_per_item['question'] == num_saved

    tags = []
    for term in items[0]['terms']:
        if term['taxonomy'] == 'tags':
            tags.append(term['name'])

    assert len(tags) > 0, "No tags were imported"
    assert tags[0] == "Lofa"
