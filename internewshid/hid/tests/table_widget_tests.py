from django.test import TestCase

from mock import patch

from hid.widgets.table import TableWidget


class TestTableWidget(TestCase):
    def test_context_data_includes_widget_title(self):
        widget = TableWidget()
        context_data = widget.get_context_data(
            title='table title'
        )
        self.assertEqual(context_data['title'], 'table title')

    def test_get_context_data_invokes_api(self):
        widget = TableWidget()
        with patch('hid.widgets.table.transport.items.list') as mock:
            widget.get_context_data()
            self.assertTrue(mock.called)

    def test_get_context_data_invokes_api_with_filters(self):
        widget = TableWidget()
        with patch('hid.widgets.table.transport.items.list') as mock:
            widget.get_context_data(filters={'a': 'b'})
            self.assertEquals(mock.call_args[1],
                              {'a': 'b', 'ordering': '-timestamp', 'limit': 10})

    def test_get_context_data_table_excludes_fields(self):
        widget = TableWidget()
        with patch('hid.widgets.table.transport.items.list') as mock:
            mock.return_value = {'results': []}
            with patch('hid.widgets.table.ItemTable') as mock_table:
                widget.get_context_data()
                excludes = mock_table.call_args[1]['exclude']
                self.assertEqual(set(excludes), set([
                    'category', 'select_item', 'network_provider'
                ]))
