import transport
from hid.tables import ItemTable


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
        # Read settings
        title = kwargs.get('title', '(no title)')
        filters = kwargs.get('filters', {})
        count = kwargs.get('count', 10)
        order_by = kwargs.get('order_by', '-timestamp')

        filters['limit'] = count
        filters['ordering'] = order_by

        response = transport.items.list(**filters)
        items = response['results']

        # Prepare table object
        table = ItemTable(
            items,
            categories=[],
            orderable=False,
            exclude=('category', 'select_item', 'network_provider')
        )

        # And return context
        return {
            'title': title,
            'table': table
        }
