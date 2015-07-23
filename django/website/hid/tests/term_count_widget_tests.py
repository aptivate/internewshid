from mock import patch
from django.test import TestCase
from hid.widgets.term_count_chart import TermCountChartWidget


class TestTermCountChartWidget(TestCase):
    def test_context_data_includes_widget_title(self):
        widget = TermCountChartWidget()
        with patch('hid.widgets.term_count_chart.term_itemcount') as itemcount:
            itemcount.return_value = []
            context_data = widget.get_context_data(
                title='test-name', taxonomy='tax'
            )
        self.assertEqual(context_data['title'], 'test-name')

    def test_context_data_includes_flot_options(self):
        widget = TermCountChartWidget()
        with patch('hid.widgets.term_count_chart.term_itemcount') as itemcount:
            itemcount.return_value = []
            context_data = widget.get_context_data(
                title='test-name', taxonomy='tax'
            )
        self.assertTrue('options' in context_data)

    def test_context_data_includes_flot_data(self):
        widget = TermCountChartWidget()
        with patch('hid.widgets.term_count_chart.term_itemcount') as itemcount:
            itemcount.return_value = []
            context_data = widget.get_context_data(
                title='test-name', taxonomy='tax'
            )
        self.assertTrue('data' in context_data)

    def test_context_data_includes_correct_data(self):
        widget = TermCountChartWidget()
        with patch('hid.widgets.term_count_chart.term_itemcount') as itemcount:
            itemcount.return_value = [
                {
                    'name': 'name one',
                    'long_name': 'long name one',
                    'count': 345
                },
                {
                    'name': 'name two',
                    'long_name': 'long name two',
                    'count': 782
                },
            ]
            context_data = widget.get_context_data(
                title='test-name', taxonomy='tax'
            )
        self.assertEqual(
            context_data['data'],
            [[[345, 2], [782, 1]]]
        )

    def test_chart_questions_are_set_as_yaxis_value_labels(self):
        widget = TermCountChartWidget()
        with patch('hid.widgets.term_count_chart.term_itemcount') as itemcount:
            itemcount.return_value = [
                {
                    'name': 'name one',
                    'long_name': 'long name one',
                    'count': 345
                },
                {
                    'name': 'name two',
                    'long_name': 'long name two',
                    'count': 782
                },
            ]
            context_data = widget.get_context_data(
                title='test-name', taxonomy='tax'
            )
        self.assertEqual(
            context_data['options']['yaxis']['ticks'],
            [[2, 'long name one'], [1, 'long name two']]
        )

    def test_fetch_counts_orders_by_long_name(self):
        widget = TermCountChartWidget()

        with patch('hid.widgets.term_count_chart.term_itemcount') as itemcount:
            itemcount.return_value = [
                {
                    'name': 'aaa-name',
                    'long_name': 'zzz-long-name',
                    'count': 0
                },
                {
                    'name': 'zzz-name',
                    'long_name': 'aaa-long-name',
                    'count': 1000
                },
            ]
            counts = widget._fetch_counts('tax', 0, 'Others')

        self.assertEqual(
            counts.items(),
            [('aaa-long-name', 1000), ('zzz-long-name', 0)]
        )
