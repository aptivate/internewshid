import datetime
import decimal
from os import path
import pytest

from django.utils.translation import ugettext as _

from .utils import (
    get_profile, get_columns_map, order_columns, get_fields_and_types,
    parse_date, normalize_row, get_rows_iterator, convert_row,
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


@pytest.mark.django_db
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
        '05-01-2015'
    )
    expected = datetime.date(2015, 1, 5)
    for date in dates:
        assert parse_date(date) == expected


def test_exception_raised_on_faulty_dates():
    bad_date = '05x01-2015'
    with pytest.raises(ValueError):
        parse_date(bad_date)


def test_convert_row():
    row = ['Short message', '5', '10.4', '1.5.2015', 'Something else']
    types = ('text', 'integer', 'number', 'date', 'ignore')

    number = decimal.Decimal('10.4')
    date = datetime.date(2015, 5, 1)

    converted = convert_row(row, types, 4)
    assert converted == ['Short message', 5, number, date]


def test_convert_row_raises_on_unknown_type():
    row = ['Short message']
    types = ['location']

    with pytest.raises(SheetImportException) as excinfo:
        convert_row(row, types, 5)
    assert excinfo.value.message == _(u"Unknown data type 'location' on row 5 ")


def test_convert_row_raises_on_malformed_value():
    row = ['not_integer']
    types = ['integer']

    with pytest.raises(SheetImportException) as excinfo:
        convert_row(row, types, 3)
    assert excinfo.value.message == _(u"Can not process value 'not_integer' of type 'integer' on row 3 ")


def test_normalize_row_differences():
    class Cell(object):
        def __init__(self, value):
            self.value = value

    row = [5, 'London', Cell('1.1.2015')]
    result = normalize_row(row)
    assert result == [5, 'London', '1.1.2015']
