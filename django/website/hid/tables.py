import django_tables2 as tables


class NamedCheckBoxColumn(tables.CheckBoxColumn):
    @property
    def header(self):
        return self.verbose_name


class ItemTable(tables.Table):
    timestamp = tables.Column(verbose_name="Created")
    body = tables.Column(verbose_name="Message")
    delete = NamedCheckBoxColumn(accessor='id', verbose_name="Delete")

    class Meta:
        attrs = {"class": "table"}
        template = "hid/table.html"
