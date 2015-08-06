from django import template
from django.template.loader import render_to_string

from ..tab_pool import get_tab


register = template.Library()


@register.simple_tag(takes_context=True)
def render_tab(context, tab_instance):
    tab = get_tab(tab_instance.view_name)

    template_name = tab.template_name

    if tab_instance.settings:
        settings = tab_instance.settings
    else:
        settings = {}  # TODO: json field doesn't default to this?

    tab_details = tab.get_context_data(**settings)

    if context:  # TODO: Only used for testing?
        request = context.get('request')
    else:
        request = None

    return render_to_string(template_name,
                            context=tab_details,
                            request=request)
