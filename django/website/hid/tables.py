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

    select_item = tables.TemplateColumn(
        template_name='hid/select_item_id_checkbox_column.html',
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

    @staticmethod
    def get_selected(params):
        """ Given a request parameter list, return the items that were
            selected using the select_item column.

            Args:
                - params: GET/POST parameter list
            Returns:
                List of selected record ids as integers
        """
        return [int(x) for x in params.getlist("select_item_id", [])]
