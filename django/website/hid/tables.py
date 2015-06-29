import django_tables2 as tables


class ItemTable(tables.Table):
    created = tables.Column(verbose_name="Imported")
    timestamp = tables.Column(verbose_name="Created")
    body = tables.Column(verbose_name="Message")

    class Meta:
        attrs = {"class": "table"}
        order_by = ('-created',)
