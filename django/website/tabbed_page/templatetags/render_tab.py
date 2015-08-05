from django.template.loader import render_to_string

from ..tab_pool import get_tab


def render_tab(tab_instance):
    tab = get_tab(tab_instance.name)

    template_name = tab.template_name

    settings = tab_instance.settings
    context = tab.get_context_data(**settings)

    return render_to_string(template_name, context)
