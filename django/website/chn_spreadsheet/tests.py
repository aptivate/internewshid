import datetime
import decimal
from os import path
import pytest
import pytz

from django.utils.translation import ugettext as _

from .utils import (
    convert_value,
    get_profile, get_columns_map, order_columns, get_fields_and_types,
    parse_date, normalize_row, get_rows_iterator, process_row, process_rows,
    save_rows, store_spreadsheet,
    SheetProfile, SheetImportException
)

from data_layer.models import Message


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


@pytest.mark.django_db
@pytest.mark.xfail
def test_get_profile_returns_profile():
    label = "unknownpoll"
    profile = {'name': 'Empty profile'}

    SheetProfile.objects.create(label=label, profile=profile)

    sprofile = get_profile(label)
    assert sprofile == profile


@pytest.mark.django_db
def test_get_profile_raises_on_unknown_label():
    with pytest.raises(SheetImportException) as excinfo:
        get_profile('unknownlabel')
    assert excinfo.value.message == _('Misconfigured service. Source "unknownlabel" does not exist')


def test_get_columns_map():
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
    result = get_columns_map(COLUMN_LIST)
    assert result == expected_result


def test_get_rows_iterator_raises_on_non_excel_files():
    with pytest.raises(SheetImportException) as excinfo:
        get_rows_iterator('not_a_file', 'excel')
    assert excinfo.value.message == _('Expected excel file. Received file in an unrecognized format.')

    with pytest.raises(SheetImportException) as excinfo:
        get_rows_iterator(None, 'pdf')
    assert excinfo.value.message == _('Unsupported file format: pdf')


def test_get_rows_iterator_works_on_excel_files():
    file_path = path.join(TEST_DIR, 'sample_excel.xlsx')
    f = open(file_path, 'rb')
    rows = list(get_rows_iterator(f, 'excel'))

    # 2x2 spreadsheet
    assert len(rows) == 2
    assert len(rows[0]) == 2
    assert len(rows[1]) == 2


def _make_columns_row(column_list):
    row = [d.copy() for d in column_list]
    for col in row:
        del col['name']  # Unify with first row version
    return row


def test_order_columns_with_no_first_row_returns_original_order():
    expected = _make_columns_row(COLUMN_LIST)
    ordered = order_columns(COLUMN_LIST)
    assert ordered == expected


def test_order_columns_with_first_row_return_first_row_order():
    cleaned = _make_columns_row(COLUMN_LIST)

    first_row = ['Message', 'Province']
    ordered = order_columns(COLUMN_LIST, first_row)
    assert ordered == [cleaned[1], cleaned[0]]


def test_get_fields_and_types():
    fields, types = get_fields_and_types(COLUMN_LIST)
    expected_types = ['location', 'text']
    expected_fields = ['message.location', 'message.content']

    assert fields == expected_fields
    assert types == expected_types


def test_successful_runs_of_parse_date():
    dates = (
        '05/01/2015',
        '5.1.2015',
        '5/1/15',
        '05-01-2015',
        datetime.datetime(2015, 1, 5, 0, 0)
    )
    expected = datetime.date(2015, 1, 5)
    for date in dates:
        assert parse_date(date) == expected


def test_exception_raised_on_faulty_dates():
    bad_date = '05x01-2015'
    with pytest.raises(ValueError):
        parse_date(bad_date)


def test_process_row():
    row = ['Short message', '5', '10.4', '1.5.2015', 'Something else']

    number = decimal.Decimal('10.4')
    date = datetime.date(2015, 5, 1)

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
            'type': 'date'
        },
        {
            'name': 'Province',
            'field': 'province',
            'type': 'ignore'
        }
    ]

    converted = process_row(row, columns)
    assert converted == {
        'message': 'Short message',
        'age': 5,
        'price': number,
        'created': date
    }


def test_convert_value_raises_on_unknown_type():
    value = 'Short message'
    type = 'location'

    with pytest.raises(SheetImportException) as excinfo:
        convert_value(value, type)
    assert excinfo.value.message == _(u"Unknown data type 'location' ")


def test_convert_value_raises_on_malformed_value():
    value = 'not_integer'
    type = 'integer'

    with pytest.raises(SheetImportException) as excinfo:
        convert_value(value, type)
    assert excinfo.value.message == _(u"Can not process value 'not_integer' of type 'integer' ")


def test_normalize_row_differences():
    class Cell(object):
        def __init__(self, value):
            self.value = value

    row = [5, 'London', Cell('1.1.2015')]
    result = normalize_row(row)
    assert result == [5, 'London', '1.1.2015']


def __test_process_rows_without_or_with_header(with_header):
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

    objects = process_rows(rows, columns, with_header)
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


def test_process_rows_without_header():
    __test_process_rows_without_or_with_header(False)


def test_process_rows_with_header():
    __test_process_rows_without_or_with_header(True)


def test_process_rows_displays_line_number_on_error():
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
        process_rows(rows, columns, with_header)

    assert excinfo.value.message == _(u"Unknown data type 'location' in row 2 ")
    assert len(excinfo.traceback) > 2, "Was expecting traceback of more than 2 lines"


@pytest.mark.django_db
def test_items_imported():
    items = Message.objects.all()
    assert len(items) == 0

    file_path = path.join(TEST_DIR, 'sample_geopoll.xlsx')
    f = open(file_path, 'rb')

    num_saved = store_spreadsheet('geopoll', f)
    assert num_saved > 0

    items = Message.objects.all()
    assert len(items) > 0


@pytest.mark.django_db
def test_date_imported_correctly():
    objects = [{
        'timestamp': datetime.datetime(2015, 6, 1)
        }]

    save_rows(objects, 'message')

    item = Message.objects.all()[0]

    print item.timestamp

    expected_date = pytz.utc.localize(datetime.datetime(2015, 6, 1))

    assert item.timestamp == expected_date
