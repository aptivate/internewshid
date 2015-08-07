from django import template
from django.template.loader import render_to_string

from ..tab_pool import (
    get_tab,
    MissingTabError,
)


register = template.Library()


@register.simple_tag(takes_context=True)
def render_tab(context, tab_instance):
    request = None

    template_name, tab_details, request = _get_rendering_details(
        context, tab_instance)

    return render_to_string(template_name,
                            context=tab_details,
                            request=request)


def _get_rendering_details(context, tab_instance):
    try:
        tab = get_tab(tab_instance.tab_type)
    except MissingTabError as e:
        return _get_error_details(e.message)

    try:
        template_name = tab.template_name
    except AttributeError:
        return _get_error_details('Missing template for %s' % tab_instance.tab_type)

    if tab_instance.settings:
        settings = tab_instance.settings
    else:
        settings = {}  # TODO: json field doesn't default to this?

    request = context.get('request')

    tab_details = tab.get_context_data(
        tab_instance, request, **settings
    )

    return template_name, tab_details, request


def _get_error_details(message):
    template_name = 'tabbed_page/tab-error.html'
    tab_details = {'error': message}

    return template_name, tab_details, None
