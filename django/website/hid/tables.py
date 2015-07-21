import django_tables2 as tables
from django.conf import settings
from django.template import loader


class NamedCheckBoxColumn(tables.CheckBoxColumn):
    @property
    def header(self):
        return self.verbose_name


class ItemTable(tables.Table):
    class Meta:
        attrs = {'class': 'table table-bordered table-hover table-striped'}
        template = 'hid/table.html'
        order_by = ('-created',)

    select_action = NamedCheckBoxColumn(accessor='id', verbose_name='Select')
    created = tables.columns.DateTimeColumn(
        verbose_name='Imported',
        format=settings.SHORT_DATETIME_FORMAT,
    )
    timestamp = tables.columns.DateTimeColumn(
        verbose_name='Created',
        format=settings.SHORT_DATETIME_FORMAT,
    )
    body = tables.Column(verbose_name='Message')
    category = tables.TemplateColumn(
        template_name='hid/categories_column.html',
        accessor='terms.0.name',
    )

    def __init__(self, *args, **kwargs):
        self.categories = kwargs.pop('categories')
        super(ItemTable, self).__init__(*args, **kwargs)

    def render_category(self, record, value):
        # TODO: Test this
        Template = loader.get_template('hid/categories_column.html')
        ctx = {
            'categories': self.categories,
            'category': value,
            'record': record
        }

        return Template.render(ctx)
