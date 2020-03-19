from django.apps import AppConfig


class HidAppConfig(AppConfig):
    name = 'hid'
    verbose_name = 'Humanitarian Information Dashboard'

    def ready(self):
        from dashboard.widget_pool import register_widget
        from hid.filters import (
            AgeRangeFilter,
            CategoryFilter,
            CollectionTypeFilter,
            ContributorFilter,
            ExternalIdFilter,
            FeedbackTypeFilter,
            GenderFilter,
            LocationFilter,
            SearchFilter,
            SubLocationFilter,
            TagsFilter,
            TimeRangeFilter,
        )
        from hid.tabs.view_and_edit_table import ViewAndEditTableTab
        from hid.widgets.term_count_chart import TermCountChartWidget
        from hid.widgets.table import TableWidget
        from tabbed_page.tab_pool import register_tab
        from tabbed_page.filter_pool import register_filter

        register_filter('category', CategoryFilter())
        register_filter('time_range', TimeRangeFilter())
        register_filter('location', LocationFilter())
        register_filter('sub_location', SubLocationFilter())
        register_filter('gender', GenderFilter())
        register_filter('age_range', AgeRangeFilter())
        register_filter('contributor', ContributorFilter())
        register_filter('collection_type', CollectionTypeFilter())
        register_filter('tags', TagsFilter())
        register_filter('feedback_type', FeedbackTypeFilter())
        register_filter('external_id', ExternalIdFilter())
        register_filter('search', SearchFilter())

        register_tab('view-and-edit-table', ViewAndEditTableTab())

        register_widget('term-count-chart', TermCountChartWidget())
        register_widget('table-widget', TableWidget())
        register_widget('question-chart-widget', TableWidget())
