import django_tables2 as tables
from django.conf import settings


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

    class Meta:
        attrs = {"class": "table"}
        order_by = ('-created',)
