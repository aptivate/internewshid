from dashboard.widget_pool import register_widget
from hid.widgets.term_count_chart import TermCountChartWidget
from hid.widgets.table import TableWidget


register_widget('term-count-chart', TermCountChartWidget())
register_widget('table-widget', TableWidget())
