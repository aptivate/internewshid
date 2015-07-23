import logging

from django import template
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from dashboard.widget_pool import get_widget, MissingWidgetType


logger = logging.getLogger(__name__)
register = template.Library()


@register.filter(name='render_widget')
def render_widget(widget_instance):
    """ Django custom template tag used to render widgets.

    The rendering is done using the template defined in the
    associated widget type. If the widget type implements
    get_context_data then that is used to generate the
    template context.
    """
    widget = None
    # Get settings, if any
    if widget_instance.settings:
        settings = widget_instance.settings
    else:
        settings = {}
    # Get widget
    try:
        widget = get_widget(widget_instance.widget_type)
    except MissingWidgetType:
        template_name = 'dashboard/widget-error.html'
        context = {}
        context['error'] = _('Unknown widget type %(widget_type)s') % {
            'widget_type': widget_instance.widget_type
        }
        context['empty_type'] = widget_instance.widget_type
    if widget:
        # Get template
        try:
            template_name = widget.template_name
        except AttributeError:
            template_name = 'dashboard/widget-error.html'
            context = {}
            context['error'] = _('Missing template for %(widget_type)s') % {
                'widget_type': widget_instance.widget_type
            }
            widget = None
    if widget:
        # Get context
        try:
            context = widget.get_context_data(**settings)
        except:
            logger.exception()
            template_name = 'dashboard/widget-error.html'
            context['error'] = _('Widget error. See error logs.')

    return render_to_string(template_name, context)
