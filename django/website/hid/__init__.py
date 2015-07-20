from dashboard.widget_pool import register_widget
from hid.widgets.chart import QuestionChartWidget
from hid.widgets.table import TableWidget


register_widget('question-chart-widget', QuestionChartWidget())
register_widget('table-widget', TableWidget())
