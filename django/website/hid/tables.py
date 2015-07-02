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
        super(ItemTable, self).__init__(*args, **kwargs)
        self.categories = self.get_categories(kwargs.get('taxonomy_id'))

    def get_categories(self, taxonomy_id=None):
        '''
        TODO: Fetch categories based on their taxonomy id
        '''
        return (
            ('first', 'First'),
            ('second', 'Second'),
            ('third', 'Third'),
            ('fourth', 'Fourth'),
        )

    def render_category(self, record, value):
        from random import randint
        rand_category = self.categories[randint(0, len(self.categories) - 1)]
        Template = loader.get_template('hid/categories_column.html')
        ctx = {
            'categories': self.categories,
            'category': rand_category[0],
            'record': record
        }
        return Template.render(ctx)
