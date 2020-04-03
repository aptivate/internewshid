import datetime

from django.utils.translation import ugettext as _

import pytest
import pytz

from ..importer import CellConverter, SheetImportException


def test_successful_runs_of_parse_date():
    dates = (
        ('05/01/2015', '%d/%m/%Y'),
        ('5.1.2015', '%d.%m.%Y'),
        ('5/1/15', '%d/%m/%y'),
        ('05-01-2015', '%d-%m-%Y'),
        (datetime.datetime(2015, 1, 5, 0, 0), None)
    )
    expected = pytz.utc.localize(datetime.datetime(2015, 1, 5))
    for date, date_format in dates:
        converter = CellConverter(date,
                                  {'type': 'date',
                                   'field': '',
                                   'date_format': date_format})

        assert converter.convert_value() == expected



@pytest.mark.skip('Note(luke): accept any type of date for now...')
def test_exception_raised_on_faulty_dates():
    bad_date = '05x01-2015'
    with pytest.raises(SheetImportException):
        converter = CellConverter(bad_date,
                                  {'type': 'date',
                                   'field': '',
                                   'date_format': '%m-%d-%Y'})
        converter.convert_value()


def test_convert_value_raises_on_unknown_type():
    value = 'Short message'
    type = 'location'

    converter = CellConverter(value, {'type': type, 'field': ''})
    with pytest.raises(SheetImportException) as excinfo:
        converter.convert_value()
    assert str(excinfo.value) == _(u"Unknown data type 'location' ")


def test_convert_value_raises_on_malformed_value():
    value = 'not_integer'
    type = 'integer'

    converter = CellConverter(value, {'type': type, 'field': ''})

    with pytest.raises(SheetImportException) as excinfo:
        converter.convert_value()

    messages = str(excinfo.value).split('\n')
    assert any((
        _(u"'not_integer' of type 'integer' ")
        in message for message in messages
    ))


def test_convert_value_raises_on_date_without_format():
    value = '1.5.2015'

    converter = CellConverter(value, {
        'type': 'date',
        'field': 'created'})

    with pytest.raises(SheetImportException) as excinfo:
        converter.convert_value()

    messages = str(excinfo.value).split('\n')
    assert any((
        _(u"Date format not specified for 'created' ")
        in message for message in messages
    ))


def test_date_can_be_empty():
    value = None

    converter = CellConverter(value, {
        'type': 'date',
        'field': 'created'})

    date = converter.convert_value()

    assert date is None


def test_taxonomy_field_converted():
    value = 'Lofa'

    converter = CellConverter(value, {
        'type': 'taxonomy',
        'field': 'terms'})

    location = converter.convert_value()

    assert location == value
