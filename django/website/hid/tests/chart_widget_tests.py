from django.test import TestCase
from hid.widgets.chart import QuestionChartWidget


class TestQuestionChartWidget(TestCase):
    def test_context_data_includes_widget_name(self):
        widget = QuestionChartWidget()
        context_data = widget.get_context_data(name='test-name', questions={})
        self.assertEqual(context_data['name'], 'test-name')

    def test_context_data_includes_flot_options(self):
        widget = QuestionChartWidget()
        context_data = widget.get_context_data(name='test-name', questions={})
        self.assertTrue('options' in context_data)

    def test_context_data_includes_flot_data(self):
        widget = QuestionChartWidget()
        context_data = widget.get_context_data(name='test-name', questions={})
        self.assertTrue('data' in context_data)

    def test_context_data_includes_correct_data(self):
        widget = QuestionChartWidget()
        context_data = widget.get_context_data(name='test-name', questions={
            'question one': 345,
            'question two': 782
        })
        self.assertEqual(
            context_data['data'],
            [[[345, 0], [782, 1]]]
        )

    def test_chart_questions_are_set_as_yaxis_value_labels(self):
        widget = QuestionChartWidget()
        context_data = widget.get_context_data(name='test-name', questions={
            'question one': 345,
            'question two': 782
        })
        self.assertEqual(
            context_data['options']['yaxis']['ticks'],
            [[0, 'question one'], [1, 'question two']]
        )
