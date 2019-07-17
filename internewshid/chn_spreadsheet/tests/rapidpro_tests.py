import datetime
from os import path

from django.core.management import call_command

import pytest
import pytz

import transport

TEST_BASE_DIR = path.abspath(path.dirname(__file__))
TEST_DIR = path.join(TEST_BASE_DIR, 'test_files')


@pytest.fixture
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command('loaddata', 'liberia-ebola.json')


@pytest.mark.django_db  # noqa
def test_items_imported(importer):
    assert len(transport.items.list()['results']) == 0

    file_path = path.join(TEST_DIR, 'sample_rapidpro.xlsx')
    f = open(file_path, 'rb')

    (num_saved, _) = importer.store_spreadsheet('rapidpro', f)
    assert num_saved > 0

    items = transport.items.list()['results']
    assert len(items) == num_saved

    assert items[0]['body'] == (
        "That there is a special budget to give money to the "
        "family of each dead in Liberia since the Ebola outbreak."
    )
    assert items[0]['timestamp'] == pytz.utc.localize(
        datetime.datetime(2015, 4, 19, 21, 35, 20))
    assert items[0]['network_provider'] == '8737 (Cellcom)'

    item_types = transport.taxonomies.term_itemcount(
        slug='item-types')

    counts_per_item = {t['name']: t['count'] for t in item_types}

    assert counts_per_item['rumor'] == num_saved

    origins = transport.taxonomies.term_itemcount(
        slug='data-origins')

    counts_per_item = {t['name']: t['count'] for t in origins}

    assert counts_per_item['Rapidpro Spreadsheet'] == num_saved

    tags = []
    for term in items[0]['terms']:
        if term['taxonomy'] == 'tags':
            tags.append(term['name'])

    assert len(tags) > 0, "No tags were imported"
    assert tags[0] == "Bomi"
