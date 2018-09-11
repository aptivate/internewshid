from django.conf import settings
from django.template import loader
from django.utils.translation import ugettext_lazy as _

import django_tables2 as tables


class NamedCheckBoxColumn(tables.CheckBoxColumn):
    @property
    def header(self):
        return self.verbose_name


class ItemTable(tables.Table):
    class Meta:
        attrs = {'class': 'table table-bordered table-hover table-striped'}
        template_name = 'hid/table.html'
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
    body = tables.TemplateColumn(
        template_name='hid/body_column.html',
        verbose_name=_('Item')
    )
    network_provider = tables.Column(
        verbose_name=_('Network Provider')
    )
    category = tables.TemplateColumn(
        verbose_name=_('Question Type'),
        template_name='hid/categories_column.html',
        accessor='terms'
    )

    def __init__(self, *args, **kwargs):
        self.categories = kwargs.pop('categories')
        super(ItemTable, self).__init__(*args, **kwargs)

    def render_category(self, record, value):
        Template = loader.get_template('hid/categories_column.html')
        selected = []
        for term in value:
            if term['taxonomy'] == 'ebola-questions':
                selected.append(term['name'])
        ctx = {
            'categories': self.categories,
            'selected': selected,
            'record': record
        }

        return Template.render(ctx)

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

    @staticmethod
    def get_row_select_values(params, input_prefix):
        """ Given a request parameter list, return the values that were
            set on each of the given rows using the given drop down or
            input field.

            Args:
                - params: GET/POST parameter list
                - input_prefix: Prefix used for each rows' input field,
                                such that the input field's name is
                                <input_prefix>-<row id>
            Returns:
                List of tuples (row id, field value)
        """
        values = []
        for name, value in params.items():
            if name.startswith(input_prefix + '-'):
                row_id = int(name[len(input_prefix)+1:])
                values.append((row_id, value))
        return values
