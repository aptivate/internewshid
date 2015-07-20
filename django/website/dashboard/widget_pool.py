_pool = {}


def register_widget(name, widget):
    """ Register a new widget type

    Args:
        name: Name of the widget type
        widget: Widget object. This should have a 'template_name'
                property, and may implement 'get_context_data(**kwargs)'
                which gets invoked with the widget settings, and the
                return value of which is set as the context of the
                template defined in template_name.
    """
    global _pool
    _pool[name] = widget


def get_widget(name):
    """ Return a named widget type

    Args:
        name: Name of the widet type
    Returns:
        The widget object as registered with register_widget
    Raises:
        KeyError: If the widget type does not exist
    """
    global _pool
    return _pool[name]


class BasicTextWidget(object):
    """ A simple text widget.

    Settings:
        title: The widget title
        text: The widget text
        html: If true, the content contains html.
              If false, the content should be escaped.
    """
    template_name = 'dashboard/basic-text-widget.html'

    def get_context_data(self, **kwargs):
        title = kwargs.get('title', '(no title')
        text = kwargs.get('text', '(no text)')
        html = kwargs.get('html', False)
        return {
            'title': title,
            'text': text,
            'html': html
        }

register_widget('basic-text-widget', BasicTextWidget())
