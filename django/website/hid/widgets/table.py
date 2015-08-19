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
        order_by = kwargs.get('order_by', None)

        # Fetch items. Eventually sorting & limiting
        # number of items will be sorted by the API.
        items = transport.items.list(**filters)
        if order_by:
            if order_by.startswith('-'):
                items.sort(key=lambda e: e[order_by[1:]], reverse=True)
            else:
                items.sort(key=lambda e: e[order_by])
        items = items[0:count]

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
