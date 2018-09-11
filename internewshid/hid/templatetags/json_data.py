import json

from django import template

register = template.Library()


@register.filter(name='json_data')
def json_data(value):
    """ Django custom template tag used to embed arbitrary
        values as json within html5 data- attributes.
    """
    return json.dumps(value)
