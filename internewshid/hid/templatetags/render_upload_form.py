from django import template
from django.template.loader import render_to_string

from hid.forms.upload import UploadForm

register = template.Library()


def build_upload_form(source, next_url):
    if source is None:
        return None

    return UploadForm(
        auto_id=False,
        initial={
            'source': source,
            'next': next_url,
        }
    )


@register.simple_tag(takes_context=True)
def render_upload_form(context, source, next_url, type_label):
    request = context['request']

    context = {
        'upload_form': build_upload_form(source, next_url),
        'type_label': type_label
    }

    return render_to_string('hid/upload_form.html',
                            context=context,
                            request=request)
