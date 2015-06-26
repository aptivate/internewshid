import django_tables2 as tables


class ItemTable(tables.Table):
    timestamp = tables.Column(verbose_name="Created")
    body = tables.Column(verbose_name="Message")

    class Meta:
        attrs = {"class": "table"}
