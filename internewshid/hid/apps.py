from django.apps import AppConfig


class HidAppConfig(AppConfig):
    name = 'hid'
    verbose_name = 'Humanitarian Information Dashboard'

    def ready(self):
        from dashboard.widget_pool import register_widget
        from hid.tabs.view_and_edit_table import ViewAndEditTableTab
        from hid.widgets.term_count_chart import TermCountChartWidget
        from hid.widgets.table import TableWidget
        from tabbed_page.tab_pool import register_tab

        register_tab('view-and-edit-table', ViewAndEditTableTab())
        register_widget('term-count-chart', TermCountChartWidget())
        register_widget('table-widget', TableWidget())
        register_widget('question-chart-widget', TableWidget())
