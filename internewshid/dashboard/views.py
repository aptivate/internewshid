from django.views.generic import TemplateView

from dashboard.models import Dashboard
from dashboard.widget_pool import MissingWidgetType, get_widget
from hid.assets import require_assets


class DashboardView(TemplateView):
    """ View to display a named dashboard """
    template_name = 'dashboard/dashboard.html'

    def get_context_data(self, **kwargs):
        """ Get the list of widgets for this dashboard, and organise them
            in row/columns to be displayed by the template.
        """
        context = super(DashboardView, self).get_context_data(**kwargs) or {}

        # Get dashboard
        if 'name' in self.kwargs and self.kwargs['name']:
            name = self.kwargs['name']
        else:
            name = 'main'
        dashboard = Dashboard.objects.get(name=name)
        context['name'] = dashboard.name

        # Get widgets and sort them by row
        widgets = dashboard.widgetinstance_set.all().order_by('row', 'column')
        context['rows'] = []
        current_row = []
        current_row_number = None
        for widget in widgets:
            if current_row_number is None:
                current_row_number = widget.row
            elif current_row_number != widget.row:
                context['rows'].append(current_row)
                current_row_number = widget.row
                current_row = []
            current_row.append(widget)
        if len(current_row) > 0:
            context['rows'].append(current_row)

        # Ensure we have all the javascript & css dependencies
        require_assets('dashboard/dashboard.css')
        for widget in widgets:
            try:
                widget_type = get_widget(widget.widget_type)
            except MissingWidgetType:
                continue
            if hasattr(widget_type, 'javascript'):
                require_assets(*widget_type.javascript)
            if hasattr(widget_type, 'css'):
                require_assets(*widget_type.css)

        # Return the context
        return context
