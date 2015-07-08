import dateutil.parser
from decimal import Decimal
import datetime
import pytz
import sys

from django.utils.timezone import is_naive
from django.utils.translation import ugettext as _
from openpyxl import load_workbook

from transport import ItemTransport

from .models import SheetProfile


class SheetImportException(Exception):
    pass


class Importer(object):

    items = ItemTransport()

    def get_profile(self, label):
        try:
            sheet_profile = SheetProfile.objects.get(label=label)
        except SheetProfile.DoesNotExist:
            error_msg = _('Misconfigured service. Source "%s" does not exist') % label
            raise SheetImportException(error_msg)

        # TODO: Revert to using database
        # return sheet_profile.profile

        return {
            "label": "geopoll",
            "name": "Geopoll",
            "format": "excel",
            "type": "message",
            "columns": [
                {
                    "name": "Province",
                    "type": "ignore",
                    "field": "ignore"
                },
                {
                    "name": "CreatedDate",
                    "type": "date",
                    "field": "timestamp",
                    "date_format": "%m/%d/%y"
                },
                {
                    "name": "AgeGroup",
                    "type": "ignore",
                    "field": "ignore"
                },
                {
                    "name": "QuestIO",
                    "type": "text",
                    "field": "body"
                }
            ],
            "skip_header": 1
        }

    def get_columns_map(self, col_list):
        '''This function assumes that column names are unique for spreadsheet.
        If they are not, then you already have a problem.'''

        columns_map = {}

        for column in col_list:
            col_dict = {
                'type': column['type'],
                'field': column['field']}

            if 'date_format' in column:
                col_dict['date_format'] = column['date_format']

            columns_map[column['name']] = col_dict

        return columns_map

    def get_rows_iterator(self, spreadsheet, file_format):
        if file_format == 'excel':
            try:
                wb = load_workbook(spreadsheet, read_only=True)
                ws = wb[wb.sheetnames[0]]
            except:
                error_msg = _('Expected excel file. Received file in an unrecognized format.')
                raise SheetImportException(error_msg)
            rows = ws.rows
        else:
            error_msg = _('Unsupported file format: %s') % file_format
            raise SheetImportException(error_msg)

        return rows

    def order_columns(self, profile_columns, first_row=None):
        columns = []
        if first_row:
            col_map = self.get_columns_map(profile_columns)
            for label in first_row:
                try:
                    columns.append(col_map[label])
                except:
                    error_msg = _('Unknown column: %s') % label
                    raise SheetImportException(error_msg)
        else:
            columns = [d.copy() for d in profile_columns]
            for col in columns:
                del col['name']  # Unify with first row version

        return columns

    def get_fields_and_types(self, columns):
        fields = [col['field'] for col in columns]
        types = [col['type'] for col in columns]

        return fields, types

    def normalize_row(self, raw_row):
        # Unify difference between CSV and openpyxl cells
        return [getattr(v, 'value', v) for v in raw_row]

    def process_rows(self, rows, profile_columns, skip_header=False):
        # If there is no header (skip_header=False), then use profile's order of
        # columns, otherwise use header line to check mapping and define order
        first_row = self.normalize_row(rows.next()) if skip_header else None
        columns = self.order_columns(profile_columns, first_row)
        # columns = [{'field': "...", 'type': "..."}, ...]

        objects = []
        for i, row in enumerate(rows, 2 if first_row else 1):
            try:
                objects.append(self.process_row(row, columns))
            except SheetImportException as e:
                raise type(e), type(e)(e.message +
                                       'in row %d ' % i), sys.exc_info()[2]

        return objects

    def process_row(self, row, columns):
        values = self.normalize_row(row)
        return reduce(
            lambda object_dict, converter: converter.add_to(object_dict),
            [CellConverter(val, col) for val, col in zip(values, columns)],
            {}
        )

    def save_rows(self, objects, data_type):
        for obj in objects:
            self.items.create(obj)

        return len(objects)

    def store_spreadsheet(self, label, fobject):
        profile = self.get_profile(label)

        file_format = profile.get('format')
        skip_header = profile.get('skip_header', False)

        rows = self.get_rows_iterator(fobject, file_format)
        items = self.process_rows(rows, profile['columns'], skip_header)

        return self.save_rows(items, 'message')


class CellConverter(object):
    def __init__(self, value, col_spec):
        self.value = value
        self.type = col_spec['type']
        self.field = col_spec['field']
        self.date_format = col_spec.get('date_format', None)

    def add_to(self, object_dict):
        if self.type != 'ignore':
            object_dict[self.field] = self.convert_value()
        return object_dict

    def convert_value(self):
        converters = {
            'date': lambda x: self.convert_date(),
            'text': lambda x: x,
            'integer': lambda x: int(x),
            'number': lambda x: Decimal(x)
        }
        if self.type not in converters:
            raise SheetImportException(
                _(u"Unknown data type '%s' ") % (self.type))
        try:
            return converters[self.type](self.value)
        except Exception as e:
            message = _("%s\nCan not process value '%s' of type '%s' ") % (e.message, self.value, self.type)
            raise SheetImportException(message), None, sys.exc_info()[2]

    def convert_date(self):
        if isinstance(self.value, basestring):
            date_time = self.parse_date()
        else:
            date_time = self.value

        if is_naive(date_time):
            date_time = pytz.utc.localize(date_time)

        return date_time

    def parse_date(self):
        if self.date_format is None:
            raise SheetImportException(
                _(u"Date format not specified for '%s' ") %
                (self.field))

        try:
            date_time = datetime.datetime.strptime(self.value,
                                                   self.date_format)
        except:
            date_time = dateutil.parser.parse(self.value)

        return date_time
