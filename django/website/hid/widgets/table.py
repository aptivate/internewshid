class TableWidget(object):
    """ A table widget.

        Eventually this should pull the table rows through the
        data API. For now we pass these in via the settings.

        Settings:
            title: Title of the table
            headers: Row of headers
            rows: Rows of data (list of lists)
            html: Set to true to indicate that the
                  headers and data contain html
                  and should not be escaped
    """
    template_name = 'hid/widgets/table.html'

    def get_context_data(self, **kwargs):
        title = kwargs.get('title', '(no title)')
        headers = kwargs.get('headers', [])
        rows = kwargs.get('rows', [])
        html = kwargs.get('html', False)
        return {
            'title': title,
            'headers': headers,
            'rows': rows,
            'html': html
        }
