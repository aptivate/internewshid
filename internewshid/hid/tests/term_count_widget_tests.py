from datetime import datetime, timedelta

from django.test import TestCase

from dateutil import parser
from mock import patch

from dashboard.widget_pool import WidgetError
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
            context_data['data'][0]['data'],
            [[345, 2], [782, 1]]
        )

    def test_context_data_hides_legend_when_there_is_no_time_period(self):
        widget = TermCountChartWidget()
        with patch('hid.widgets.term_count_chart.term_itemcount') as itemcount:
            itemcount.return_value = []
            context_data = widget.get_context_data(
                title='test-name', taxonomy='tax'
            )
        self.assertEqual(context_data['options']['legend']['show'], False)

    def test_context_data_includes_legend_when_there_is_a_time_period(self):
        widget = TermCountChartWidget()
        with patch('hid.widgets.term_count_chart.term_itemcount') as itemcount:
            itemcount.return_value = []
            periods = [{
                'start_time': '2015-01-01',
                'end_time': '2015-02-02'
            }]
            context_data = widget.get_context_data(
                title='test-name', taxonomy='tax', periods=periods
            )
        self.assertEqual(context_data['options']['legend']['show'], True)

    def test_context_data_raises_widgeterror_when_more_than_one_period(self):
        widget = TermCountChartWidget()
        with patch('hid.widgets.term_count_chart.term_itemcount') as itemcount:
            itemcount.return_value = []
            periods = [{
                'start_time': '2015-01-01',
                'end_time': '2015-02-02'
            }, {
                'start-time': '2015-07-08',
                'end-time': '2015-07-09'
            }]
            with self.assertRaises(WidgetError):
                widget.get_context_data(
                    title='test-name', taxonomy='tax', periods=periods
                )

    def test_context_data_raises_widgeterror_when_date_is_not_parseable(self):
        widget = TermCountChartWidget()
        with patch('hid.widgets.term_count_chart.term_itemcount') as itemcount:
            itemcount.return_value = []
            periods = [{
                'start_time': '!!!',
                'end_time': '2015-02-02'
            }, {
                'start-time': '2015-07-08',
                'end-time': '2015-07-09'
            }]
            with self.assertRaises(WidgetError):
                widget.get_context_data(
                    title='test-name', taxonomy='tax', periods=periods
                )

    def test_get_context_data_parses_dates(self):
        widget = TermCountChartWidget()
        with patch('hid.widgets.term_count_chart.term_itemcount') as itemcount:
            itemcount.return_value = []
            periods = [{
                'start_time': '2015-01-01',
                'end_time': '2015-02-02'
            }]
            widget.get_context_data(
                title='test-name', taxonomy='tax', periods=periods
            )
            kwargs = itemcount.call_args[1]

        self.assertEqual(kwargs['start_time'], parser.parse('2015-01-01'))
        self.assertEqual(kwargs['end_time'], parser.parse('2015-02-02'))

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
            counts = widget._fetch_counts('tax', 0, None, None, 'Others')

        self.assertEqual(
            list(counts.items()),
            [('aaa-long-name', 1000), ('zzz-long-name', 0)]
        )

    def test_fetch_counts_gets_n_larger_and_aggregates_others_items(self):
        widget = TermCountChartWidget()

        with patch('hid.widgets.term_count_chart.term_itemcount') as itemcount:
            itemcount.return_value = [
                {
                    'name': 'name one',
                    'long_name': 'long-name one',
                    'count': 1
                },
                {
                    'name': 'name two',
                    'long_name': 'long-name two',
                    'count': 10
                },
                {
                    'name': 'name three',
                    'long_name': 'long-name three',
                    'count': 20
                },
                {
                    'name': 'name four',
                    'long_name': 'long-name four',
                    'count': 30
                },

            ]
            counts = widget._fetch_counts('tax', 3, None, None, 'Others')

        self.assertEqual(
            list(counts.items()),
            [
                ('long-name four', 30), ('long-name three', 20),
                ('Others', 11)
            ]
        )

    def test_fetch_count_ignores_missing_start_and_end_time(self):
        widget = TermCountChartWidget()

        with patch('hid.widgets.term_count_chart.term_itemcount') as itemcount:
            widget._fetch_counts('tax', 3, None, None, 'Others')
            itemcount_kwargs = itemcount.call_args[1]

        self.assertNotIn('start_time', itemcount_kwargs)
        self.assertNotIn('end_time', itemcount_kwargs)

    def test_fetch_count_uses_start_and_end_time(self):
        widget = TermCountChartWidget()
        t1 = datetime.now()
        t2 = t1 + timedelta(days=4)
        with patch('hid.widgets.term_count_chart.term_itemcount') as itemcount:
            widget._fetch_counts('tax', 3, t1, t2, 'Others')
            itemcount_kwargs = itemcount.call_args[1]

        self.assertEqual(t1, itemcount_kwargs['start_time'])
        self.assertEqual(t2, itemcount_kwargs['end_time'])

    def test_categories_can_be_excluded(self):
        widget = TermCountChartWidget()

        with patch('hid.widgets.term_count_chart.term_itemcount') as itemcount:
            itemcount.return_value = [
                {
                    'name': 'Ebola updates',
                    'long_name': 'What are the current updates on Ebola.',
                    'count': 0,
                },
                {
                    'name': 'Ebola prevention',
                    'long_name': 'What measures could be put in place to end Ebola.',
                    'count': 4,
                },
                {
                    'name': 'Liberia Ebola-free',
                    'long_name': 'Can Liberia be Ebola free.',
                    'count': 3,
                },
                {
                    'name': 'Unknown',
                    'long_name': 'Unknown.',
                    'count': 2,
                },
            ]
            context_data = widget.get_context_data(
                title='test-name', taxonomy='tax',
                exclude_categories=['Unknown', 'Liberia Ebola-free']
            )
        ticks = context_data['options']['yaxis']['ticks']
        labels = [t[1] for t in ticks]
        self.assertIn('What are the current updates on Ebola.', labels)
        self.assertIn('What measures could be put in place to end Ebola.',
                      labels)
        self.assertNotIn('Can Liberia be Ebola free.', labels)
        self.assertNotIn('Unknown.', labels)
