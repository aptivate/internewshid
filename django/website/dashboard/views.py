from django.views.generic import TemplateView

from dashboard.models import Dashboard
from dashboard.widget_pool import get_widget


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

        # Get all the javascript & css dependencies
        context['javascript'] = []
        context['css'] = ['dashboard/dashboard.css']
        for widget in widgets:
            widget_type = get_widget(widget.widget_type)
            if hasattr(widget_type, 'javascript'):
                context['javascript'] += widget_type.javascript
            if hasattr(widget_type, 'css'):
                context['css'] += widget_type.css
        context['javascript'] = self._remove_duplicates(context['javascript'])
        context['css'] = self._remove_duplicates(context['css'])

        # Return the context
        return context

    def _remove_duplicates(self, the_list):
        """ Remove duplicates whilst preseving order """
        out = []
        for e in the_list:
            if e not in out:
                out.append(e)
        return out
