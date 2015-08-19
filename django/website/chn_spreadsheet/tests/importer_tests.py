import datetime
import decimal
from os import path
import pytest
import pytz

from django.utils.translation import ugettext as _

import transport

from ..importer import (
    Importer,
    SheetProfile, SheetImportException
)

TEST_BASE_DIR = path.abspath(path.dirname(__file__))
TEST_DIR = path.join(TEST_BASE_DIR, 'test_files')


COLUMN_LIST = [
    {
        'name': 'Province',
        'type': 'location',
        'field': 'message.location',
    },
    {
        'name': 'Message',
        'type': 'text',
        'field': 'message.content',
    },
]


@pytest.fixture
def importer():
    return Importer()


@pytest.mark.django_db
def test_get_profile_returns_profile(importer):
    label = "unknownpoll"
    profile = {'name': 'Empty profile'}

    SheetProfile.objects.create(label=label, profile=profile)

    sprofile = importer.get_profile(label)
    assert sprofile == profile


@pytest.mark.django_db
def test_get_profile_raises_on_unknown_label(importer):

    with pytest.raises(SheetImportException) as excinfo:
        importer.get_profile('unknownlabel')
    assert excinfo.value.message == _('Misconfigured service. Source "unknownlabel" does not exist')


def test_get_columns_map(importer):
    expected_result = {
        'Province': {
            'type': 'location',
            'field': 'message.location'
        },
        'Message': {
            'type': 'text',
            'field': 'message.content'
        },
    }

    result = importer.get_columns_map(COLUMN_LIST)

    assert result == expected_result


def test_get_rows_iterator_raises_on_non_excel_files(importer):

    with pytest.raises(SheetImportException) as excinfo:
        importer.get_rows_iterator('not_a_file', 'excel')
    assert excinfo.value.message == _('Expected excel file. Received file in an unrecognized format.')

    with pytest.raises(SheetImportException) as excinfo:
        importer.get_rows_iterator(None, 'pdf')
    assert excinfo.value.message == _('Unsupported file format: pdf')


def test_get_rows_iterator_works_on_excel_files(importer):

    file_path = path.join(TEST_DIR, 'sample_excel.xlsx')
    f = open(file_path, 'rb')
    rows = list(importer.get_rows_iterator(f, 'excel'))

    # 2x2 spreadsheet
    assert len(rows) == 2
    assert len(rows[0]) == 2
    assert len(rows[1]) == 2


def _make_columns_row(column_list):
    row = [d.copy() for d in column_list]
    for col in row:
        del col['name']  # Unify with first row version
    return row


def test_order_columns_with_no_first_row_returns_original_order(importer):
    expected = _make_columns_row(COLUMN_LIST)
    ordered = importer.order_columns(COLUMN_LIST)
    assert ordered == expected


def test_order_columns_with_first_row_return_first_row_order(importer):
    cleaned = _make_columns_row(COLUMN_LIST)

    first_row = ['Message', 'Province']

    ordered = importer.order_columns(COLUMN_LIST, first_row)
    assert ordered == [cleaned[1], cleaned[0]]


def test_order_columns_ignores_extra_columns_in_first_row(importer):
    cleaned = _make_columns_row(COLUMN_LIST)
    first_row = ['Message', 'Province', 'None', 'None', 'None']

    ordered = importer.order_columns(COLUMN_LIST, first_row)

    assert ordered == [cleaned[1], cleaned[0]]


def test_get_fields_and_types(importer):
    fields, types = importer.get_fields_and_types(COLUMN_LIST)
    expected_types = ['location', 'text']
    expected_fields = ['message.location', 'message.content']

    assert fields == expected_fields
    assert types == expected_types


def test_process_row(importer):
    row = ['Short message', '5', '10.4', '1.5.2015', 'Something else']

    number = decimal.Decimal('10.4')
    date = pytz.utc.localize(datetime.datetime(2015, 5, 1))

    columns = [
        {
            'name': 'Message',
            'field': 'message',
            'type': 'text'
        },
        {
            'name': 'Age',
            'field': 'age',
            'type': 'integer'
        },
        {
            'name': 'Cost',
            'field': 'price',
            'type': 'number'
        },
        {
            'name': 'CreatedDate',
            'field': 'created',
            'type': 'date',
            'date_format': '%d.%m.%Y'
        },
        {
            'name': 'Province',
            'field': 'province',
            'type': 'ignore'
        }
    ]

    converted = importer.process_row(row, columns)
    assert converted == {
        'message': 'Short message',
        'age': 5,
        'price': number,
        'created': date
    }


def test_normalize_row_differences(importer):
    class Cell(object):
        def __init__(self, value):
            self.value = value

    row = [5, 'London', Cell('1.1.2015')]
    result = importer.normalize_row(row)
    assert result == [5, 'London', '1.1.2015']


def __test_process_rows_without_or_with_header(importer, with_header):
    def _rows_generator():
        rows = [
            ('Province', 'Message'),
            ('London', 'Short message'),
            ('Cambridge', 'What?'),
        ]
        if not with_header:
            rows = rows[1:]
        for row in rows:
            yield row

    columns = [d.copy() for d in COLUMN_LIST]
    columns[0]['type'] = 'text'
    rows = _rows_generator()

    objects = importer.process_rows(rows, columns, with_header)
    expected_objects = [
        {
            'message.location': 'London',
            'message.content': 'Short message'
        },
        {
            'message.location': 'Cambridge',
            'message.content': 'What?'
        },
    ]

    assert objects == expected_objects


def test_process_rows_without_header(importer):
    __test_process_rows_without_or_with_header(importer, False)


def test_process_rows_with_header(importer):
    __test_process_rows_without_or_with_header(importer, True)


def test_process_rows_displays_line_number_on_error(importer):
    def _rows_generator():
        rows = [
            ('Province', 'Message'),
            ('London', 'Short message'),
            ('Cambridge', 'What?'),
        ]

        for row in rows:
            yield row

    columns = [d.copy() for d in COLUMN_LIST]
    columns[0]['type'] = 'location'
    rows = _rows_generator()

    with_header = True
    with pytest.raises(SheetImportException) as excinfo:
        importer.process_rows(rows, columns, with_header)

    assert excinfo.value.message == _(u"Unknown data type 'location' in row 2 ")
    assert len(excinfo.traceback) > 2, "Was expecting traceback of more than 2 lines"


def test_process_rows_ignores_empty_lines(importer):
    class Cell(object):
        def __init__(self, value):
            self.value = value

    def _rows_generator():
        rows = [
            ('Province', 'Message'),
            ('London', 'Short message'),
            ('', ''),
            (None, None),
            (Cell(''), Cell('')),
            (Cell(None), Cell(None)),
            ('Cambridge', 'What?'),
        ]

        for row in rows:
            yield row

    column_list = [
        {
            'name': 'Province',
            'type': 'text',
            'field': 'location',
        },
        {
            'name': 'Message',
            'type': 'text',
            'field': 'body',
        },
    ]

    columns = [d.copy() for d in column_list]
    rows = _rows_generator()

    with_header = True

    objects = importer.process_rows(rows, columns, with_header)

    expected_objects = [
        {
            'location': 'London',
            'body': 'Short message'
        },
        {
            'location': 'Cambridge',
            'body': 'What?'
        },
    ]

    assert objects == expected_objects


@pytest.mark.django_db
def test_save_rows_creates_item_with_term(importer):
    objects = [{'body': "Text", 'timestamp': datetime.datetime(2014, 7, 21)}]
    assert importer.save_rows(objects, 'question') == 1

    item_types = transport.taxonomies.term_itemcount(
        slug='item-types')

    counts_per_item = {t['name']: t['count'] for t in item_types}

    assert counts_per_item['question'] == 1
    assert counts_per_item['rumor'] == 0
