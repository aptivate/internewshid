import django_tables2 as tables
from django.conf import settings


class NamedCheckBoxColumn(tables.CheckBoxColumn):
    @property
    def header(self):
        return self.verbose_name


class ItemTable(tables.Table):
    created = tables.columns.DateTimeColumn(
        verbose_name="Imported",
        format=settings.SHORT_DATETIME_FORMAT,
    )
    timestamp = tables.columns.DateTimeColumn(
        verbose_name="Created",
        format=settings.SHORT_DATETIME_FORMAT,
    )
    body = tables.Column(verbose_name="Message")
    delete = NamedCheckBoxColumn(accessor='id', verbose_name="Delete")

    class Meta:
        attrs = {"class": "table"}
        template = "hid/table.html"
        order_by = ('-created',)
