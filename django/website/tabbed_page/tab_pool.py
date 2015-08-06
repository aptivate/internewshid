_pool = {}


class MissingTabError(Exception):
    pass


def register_tab(name, tab):
    global _pool
    _pool[name] = tab


def get_tab(name):
    global _pool

    try:
        return _pool[name]
    except KeyError:
        raise MissingTabError()


def clear_tabs():
    # Currently only used in test code
    global _pool

    _pool = {}


class BasicHtmlTab(object):
    """ A simple tab to display html

    Settings:
        title: The title of the tab
            (in the header, not in
             the tab)
        body: The tab html
    """
    template_name = 'tabbed_page/basic_html_tab.html'

    def get_context_data(self, **kwargs):
        title = kwargs.get('title', '(no title)')
        body = kwargs.get('body', '(no body)')
        return {
            'title': title,
            'body': body
        }


register_tab('basic-html-tab', BasicHtmlTab())
