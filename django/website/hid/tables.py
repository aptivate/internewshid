import django_tables2 as tables
from django.conf import settings
from django.template import loader


class NamedCheckBoxColumn(tables.CheckBoxColumn):
    @property
    def header(self):
        return self.verbose_name


class ItemTable(tables.Table):
    class Meta:
        attrs = {'class': 'table'}
        template = 'hid/table.html'
        order_by = ('-created',)

    created = tables.columns.DateTimeColumn(
        verbose_name='Imported',
        format=settings.SHORT_DATETIME_FORMAT,
    )
    timestamp = tables.columns.DateTimeColumn(
        verbose_name='Created',
        format=settings.SHORT_DATETIME_FORMAT,
    )
    body = tables.Column(verbose_name='Message')
    category = tables.TemplateColumn(template_name='hid/categories_column.html')
    delete = NamedCheckBoxColumn(accessor='id', verbose_name='Delete')

    def __init__(self, *args, **kwargs):
        self.categories = kwargs.pop('categories')
        super(ItemTable, self).__init__(*args, **kwargs)

    def render_category(self, record, value):
        Template = loader.get_template('hid/categories_column.html')
        ctx = {
            'categories': self.categories,
            'category': self.categories[2][0],
            'record': record
        }
        return Template.render(ctx)
