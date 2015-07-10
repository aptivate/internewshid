from django import template
from django.template.loader import render_to_string

from dashboard.widget_pool import get_widget


register = template.Library()


@register.filter(name='render_widget')
def render_widget(widget_instance):
    """ Django custom template tag used to render widgets.

    The rendering is done using the template defined in the
    associated widget type. If the widget type implements
    get_context_data then that is used to generate the
    template context.
    """
    widget = get_widget(widget_instance.widget_type)
    if widget_instance.settings:
        settings = widget_instance.settings
    else:
        settings = {}
    try:
        context = widget.get_context_data(**settings)
    except AttributeError:
        context = {}
    try:
        template_name = widget.template_name
    except AttributeError:
        template_name = 'dashboard/widget-missing-template.html'
        context['empty_type'] = widget_instance.widget_type
    return render_to_string(template_name, context)
