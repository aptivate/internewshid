from django.test import TestCase
from hid.widgets.table import TableWidget


class TestTableWidget(TestCase):
    def test_context_data_includes_widget_title(self):
        widget = TableWidget()
        context_data = widget.get_context_data(
            title='table title'
        )
        self.assertEqual(context_data['title'], 'table title')

    def test_context_data_includes_headers(self):
        widget = TableWidget()
        context_data = widget.get_context_data(
            headers=['header one', 'header two']
        )
        self.assertEqual(context_data['headers'], [
            'header one', 'header two'
        ])

    def test_context_data_includes_rows(self):
        widget = TableWidget()

        context_data = widget.get_context_data(
            rows=[
                ['row one, col one', 'row one, col two'],
                ['row two, col one', 'row two, col two']
            ]
        )
        self.assertEqual(context_data['rows'], [
            ['row one, col one', 'row one, col two'],
            ['row two, col one', 'row two, col two']
        ])
