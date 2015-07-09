from django.views.generic import TemplateView

from dashboard.models import Dashboard


class DashboardView(TemplateView):
    """ View to display a named dashboard """
    template_name = "dashboard/dashboard.html"

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

        # Get widgets
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

        # Return the context
        return context
