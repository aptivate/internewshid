import django_tables2 as tables
from django.conf import settings
from django.utils.translation import ugettext_lazy as _


class NamedCheckBoxColumn(tables.CheckBoxColumn):
    @property
    def header(self):
        return self.verbose_name


class ItemTable(tables.Table):
    class Meta:
        attrs = {'class': 'table table-bordered table-hover table-striped'}
        template = 'hid/table.html'
        order_by = ('-created',)

    select_action = tables.TemplateColumn(
        template_name='hid/custom_checkbox.html',
        verbose_name=_('Select')
    )
    created = tables.columns.DateTimeColumn(
        verbose_name=_('Imported'),
        format=settings.SHORT_DATETIME_FORMAT,
    )
    timestamp = tables.columns.DateTimeColumn(
        verbose_name=_('Created'),
        format=settings.SHORT_DATETIME_FORMAT,
    )
    body = tables.Column(verbose_name=_('Message'))
    category = tables.Column(
        verbose_name=_('Category'),
        accessor='terms.0.name',
        default=_('Uncategorized')
    )

    def __init__(self, *args, **kwargs):
        self.categories = kwargs.pop('categories')
        super(ItemTable, self).__init__(*args, **kwargs)
