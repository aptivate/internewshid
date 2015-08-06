from django import template
from django.template.loader import render_to_string

from ..tab_pool import get_tab


register = template.Library()


@register.filter(name='render_tab')
def render_tab(tab_instance):
    tab = get_tab(tab_instance.view_name)

    template_name = tab.template_name

    if tab_instance.settings:
        settings = tab_instance.settings
    else:
        settings = {}  # TODO: json field doesn't default to this?

    context = tab.get_context_data(**settings)

    return render_to_string(template_name, context)
