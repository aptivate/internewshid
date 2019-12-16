import datetime
import decimal
from os import path

from django.utils.translation import ugettext as _

import pytest
import pytz

import transport

from ..importer import Importer, SheetImportException, SheetProfile

TEST_BASE_DIR = path.abspath(path.dirname(__file__))
TEST_DIR = path.join(TEST_BASE_DIR, 'test_files')

COLUMN_LIST = [
    {
        'name': 'Province',
        'type': 'location',
        'field': 'message.location',
    },
    {
        'name': 'Sub-Province',
        'type': 'location',
        'field': 'message.sub_location',
    },
    {
        'name': 'Message',
        'type': 'text',
        'field': 'message.content',
    },
]


@pytest.fixture
def importer():
    importer = Importer()

    importer.profile = {
        'columns': [d.copy() for d in COLUMN_LIST]
    }

    return importer


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
    assert str(excinfo.value) == _('Misconfigured service. Source "unknownlabel" does not exist')


def test_get_columns_map(importer):
    expected_result = {
        'Province': {
            'type': 'location',
            'field': 'message.location',
            'name': 'Province',
        },
        'Sub-Province': {
            'type': 'location',
            'field': 'message.sub_location',
            'name': 'Sub-Province',
        },
        'Message': {
            'type': 'text',
            'field': 'message.content',
            'name': 'Message',
        },
    }

    result = importer.get_columns_map()

    assert result == expected_result


def test_get_rows_iterator_raises_on_non_excel_files(importer):

    with pytest.raises(SheetImportException) as excinfo:
        importer.get_rows_iterator('not_a_file', 'excel')
    assert str(excinfo.value) == _('Expected excel file. Received file in an unrecognized format.')

    with pytest.raises(SheetImportException) as excinfo:
        importer.get_rows_iterator(None, 'pdf')
    assert str(excinfo.value) == _('Unsupported file format: pdf')


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

    return row


def test_order_columns_with_no_first_row_returns_original_order(importer):
    importer.profile['skip_header'] = False

    expected = _make_columns_row(COLUMN_LIST)

    ordered = importer.order_columns()

    assert ordered == expected


def test_order_columns_with_first_row_return_first_row_order(importer):
    cleaned = _make_columns_row(COLUMN_LIST)

    first_row = ['Message', 'Province', 'Sub-Province']

    importer.profile['skip_header'] = True
    ordered = importer.order_columns(first_row)

    assert ordered == [cleaned[2], cleaned[0], cleaned[1]]


def test_order_columns_ignores_extra_columns_in_first_row(importer):
    cleaned = _make_columns_row(COLUMN_LIST)
    first_row = ['Message', 'Province', 'Sub-Province', 'None', 'None', 'None']

    ordered = importer.order_columns(first_row)

    assert ordered == [cleaned[2], cleaned[0], cleaned[1]]


def test_order_columns_ignores_none_and_missing_columns_in_first_row(importer):
    first_row = ['Province', None]

    ordered = importer.order_columns(first_row)

    assert len(ordered) == 1
    assert ordered[0]['name'] == 'Province'


def test_get_fields_and_types(importer):
    fields, types = importer.get_fields_and_types(COLUMN_LIST)
    expected_types = ['location', 'location', 'text']
    expected_fields = ['message.location', 'message.sub_location', 'message.content']

    assert fields == expected_fields
    assert types == expected_types


def test_process_row(importer):
    row = [
        'Short message',
        '5',
        '10.4',
        '1.5.2015',
        'Something else',
        'Montserrado',
    ]

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
        },
        {
            'name': 'Location',
            'type': 'taxonomy',
            'field': 'terms',
            'taxonomy': 'tags',
        }
    ]

    converted = importer.process_row(row, columns)
    assert converted == {
        'message': 'Short message',
        'age': 5,
        'price': number,
        'created': date,
        'terms': [
            {
                'name': 'Montserrado',
                'taxonomy': 'tags',
            }
        ]
    }


def test_normalize_row_differences(importer):

    class Cell(object):

        def __init__(self, value):
            self.value = value

    row = [5, 'London', Cell('1.1.2015')]
    result = importer.normalize_row(row)
    assert result == [5, 'London', '1.1.2015']


def test_process_rows_with_header(importer):

    def _rows_generator():
        rows = [
            ('Province', 'Message'),
            ('London', 'Short message'),
            ('Cambridge', 'What?'),
        ]

        for row in rows:
            yield row

    columns = [d.copy() for d in COLUMN_LIST]
    columns[0]['type'] = 'text'

    importer.profile['columns'] = columns
    importer.profile['skip_header'] = True
    importer.profile['taxonomies'] = {'item-types': 'question'}

    rows = _rows_generator()
    objects = importer.process_rows(rows)

    assert objects[0]['message.location'] == 'London'
    assert objects[0]['message.content'] == 'Short message'
    assert objects[1]['message.location'] == 'Cambridge'
    assert objects[1]['message.content'] == 'What?'


def test_process_rows_without_header(importer):

    def _rows_generator():
        rows = [
            ('London', 'WithinLondon', 'Short message'),
            ('Cambridge', 'WithinCambridge', 'What?'),
        ]

        for row in rows:
            yield row

    columns = [d.copy() for d in COLUMN_LIST]
    columns[0]['type'] = 'text'
    columns[1]['type'] = 'text'
    rows = _rows_generator()

    importer.profile['columns'] = columns
    importer.profile['skip_header'] = False
    importer.profile['taxonomies'] = {'item-types': 'question'}

    objects = importer.process_rows(rows)

    assert objects[0]['message.location'] == 'London'
    assert objects[0]['message.content'] == 'Short message'

    assert objects[1]['message.location'] == 'Cambridge'
    assert objects[1]['message.content'] == 'What?'


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

    importer.profile['columns'] = columns
    importer.profile['skip_header'] = True
    importer.profile['taxonomies'] = {'item-types': 'question'}

    with pytest.raises(SheetImportException) as excinfo:
        importer.process_rows(rows)

    assert str(excinfo.value) == _(u"Unknown data type 'location' in row 2 ")
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

    importer.profile['columns'] = columns
    importer.profile['skip_header'] = True
    importer.profile['taxonomies'] = {'item-types': 'question'}

    objects = importer.process_rows(rows)

    expected_objects = [
        {
            'location': 'London',
            'body': 'Short message',
            'terms': [{'name': 'question', 'taxonomy': 'item-types'}],
            '_row_number': 2,
        },
        {
            'location': 'Cambridge',
            'body': 'What?',
            'terms': [{'name': 'question', 'taxonomy': 'item-types'}],
            '_row_number': 7,
        },
    ]

    assert objects == expected_objects


@pytest.mark.django_db
def test_save_rows_creates_item_with_term(importer):
    objects = [
        {
            'body': "Text",
            'timestamp': datetime.datetime(2014, 7, 21),
            'terms': [{
                'name': 'question',
                'taxonomy': 'item-types',
            }],
        }
    ]

    assert importer.save_rows(objects) == 1

    item_types = transport.taxonomies.term_itemcount(
        slug='item-types')

    counts_per_item = {t['name']: t['count'] for t in item_types}

    assert counts_per_item['question'] == 1
    assert counts_per_item['rumor'] == 0


@pytest.mark.django_db
def test_save_rows_handles_exception(importer):
    invalid_enumerator = "Yakub=Aara smart card no point in Kialla hoi lay smart card hoday yan gor Sara Thor Sara ,hetalli bolli aara loi bolla nosir ,zodi aara Thor Sara oi tum aara smart card loi tum .Aara tum Thor asi day yan bishi manshe zani ar bishi goba asi ,Bormar shorkari aarari zeyan hor yan oilday hetarar bolor hota .kinto hetarar aarari forok gorid day ,zodi Burmar shor karotum soyi ensaf takito aarari Thor Sara nohoito"

    objects = [
        {
            'body': "Text",
            'timestamp': datetime.datetime(2014, 7, 21),
            'enumerator': invalid_enumerator,
            'terms': [],
            '_row_number': 29,
        }
    ]

    importer.profile['columns'] = [
        {
            'name': 'Ennumerator',
            'type': 'text',
            'field': 'enumerator',
        },
    ]

    with pytest.raises(SheetImportException) as excinfo:
        importer.save_rows(objects)

    assert str(excinfo.value) == (
        "There was a problem with row 29 of the spreadsheet:\n"
        "Column: 'Ennumerator' (enumerator)\n"
        "Error (max_length): 'Ensure this field has no more "
        "than 190 characters.'\n\n"
        "Value: Yakub=Aara smart card no point in "
        "Kialla hoi lay smart card hoday yan gor Sara Thor Sara ,hetalli "
        "bolli aara loi bolla nosir ,zodi aara Thor Sara oi tum aara smart "
        "card loi tum .Aara tum Thor asi day yan bishi manshe zani ar bishi "
        "goba asi ,Bormar shorkari aarari zeyan hor yan oilday hetarar bolor "
        "hota .kinto hetarar aarari forok gorid day ,zodi Burmar shor karotum "
        "soyi ensaf takito aarari Thor Sara nohoito"
    )


@pytest.mark.django_db
def test_duplicate_records_not_imported(importer):
    objects = [
        {
            'body': "Text",
            'timestamp': datetime.datetime(2014, 7, 21),
            'enumerator': 'Mohammed',
            'terms': [],
            '_row_number': 1,
        }
    ]

    num_saved = importer.save_rows(objects)
    assert num_saved == 1

    objects = [
        # This one should be ignored the second time around
        {
            'body': "Text",
            'timestamp': datetime.datetime(2014, 7, 21),
            'enumerator': 'Mohammed',
            'terms': [],
            '_row_number': 1,
        },
        # and this one should be imported
        {
            'body': "Another bit of Text",
            'timestamp': datetime.datetime(2014, 7, 21),
            'enumerator': 'Mohammed',
            'terms': [],
            '_row_number': 2,
        }
    ]

    num_saved = importer.save_rows(objects)

    assert num_saved == 1

    items = transport.items.list_items()

    assert len(items['results']) == 2


@pytest.mark.django_db
def test_can_save_rows_without_terms(importer):
    objects = [
        {
            'body': "Text",
            'timestamp': datetime.datetime(2014, 7, 21),
            'enumerator': 'Mohammed',
            '_row_number': 1,
        }
    ]

    num_saved = importer.save_rows(objects)

    assert num_saved == 1


def test_terms_in_row_split_on_comma(importer):
    row = [
        'Tag 1, Tag 2',
    ]

    columns = [
        {
            'name': 'Tags',
            'type': 'taxonomy',
            'field': 'terms',
            'taxonomy': 'tags',
        }
    ]

    converted = importer.process_row(row, columns)
    assert converted == {
        'terms': [
            {
                'name': 'Tag 1',
                'taxonomy': 'tags',
            },
            {
                'name': 'Tag 2',
                'taxonomy': 'tags',
            },
        ]
    }
