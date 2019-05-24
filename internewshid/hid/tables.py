from django.template import loader
from django.utils.translation import ugettext_lazy as _

import django_tables2 as tables

from hid.constants import ITEM_TYPE_CATEGORY


class NamedCheckBoxColumn(tables.CheckBoxColumn):
    @property
    def header(self):
        return self.verbose_name


class ItemTable(tables.Table):
    class Meta:
        attrs = {'class': 'table table-hover table-striped', 'cols': '11'}
        template_name = 'hid/table.html'
        order_by = ('-timestamp',)

    select_item = tables.TemplateColumn(
        template_name='hid/select_item_id_checkbox_column.html',
        verbose_name=_('Select'),
        attrs={'th': {'id': 'header-select'}}
    )
    created = tables.columns.TemplateColumn(
        template_name='hid/created_column.html',
        verbose_name=_('Imported'),
        attrs={'th': {'id': 'header-imported'}}
    )
    timestamp = tables.columns.TemplateColumn(
        template_name='hid/timestamp_column.html',
        verbose_name=_('Created'),
        attrs={'th': {'id': 'header-created'}}
    )
    body = tables.TemplateColumn(
        template_name='hid/body_column.html',
        verbose_name=_('Feedback'),
        attrs={'th': {'id': 'header-feedback'}}
    )
    translation = tables.TemplateColumn(
        template_name='hid/translation_column.html',
        verbose_name=_('Translation'),
        attrs={'th': {'id': 'header-translation'}}
    )
    category = tables.TemplateColumn(
        verbose_name=_('Theme'),
        template_name='hid/categories_column.html',
        accessor='terms',
        attrs={'th': {'id': 'header-theme'}}
    )
    tags = tables.TemplateColumn(
        verbose_name=_('Tags'),
        template_name='hid/tags_column.html',
        accessor='terms',
        attrs={'th': {'id': 'header-tag'}}
    )
    feedback_type = tables.TemplateColumn(
        template_name='hid/feedback_type_column.html',
        verbose_name=_('Type'),
        accessor='terms',
        attrs={'th': {'id': 'header-type', 'title': 'Feedback type'}}
    )
    gender = tables.TemplateColumn(
        template_name='hid/gender_column.html',
        verbose_name=_('Gender'),
        attrs={'th': {'id': 'header-gender'}}
    )
    age = tables.TemplateColumn(
        template_name='hid/age_column.html',
        verbose_name=_('Age'),
        attrs={'th': {'id': 'header-age'}}
    )
    location = tables.TemplateColumn(
        template_name='hid/location_column.html',
        verbose_name=_('Location'),
        attrs={'th': {'id': 'header-location'}}
    )
    enumerator = tables.TemplateColumn(
        template_name='hid/enumerator_column.html',
        verbose_name=_('Enumerator'),
        attrs={'th': {'id': 'header-enumerator'}}
    )
    source = tables.TemplateColumn(
        template_name='hid/source_column.html',
        verbose_name=_('Source'),
        attrs={'th': {'id': 'header-source'}}
    )
    external_id = tables.TemplateColumn(
        template_name='hid/external_id_column.html',
        verbose_name=_('ID'),
        attrs={'th': {'id': 'header-external-id'}}
    )

    def __init__(self, *args, **kwargs):
        self.categories = kwargs.pop('categories', [])
        super(ItemTable, self).__init__(*args, **kwargs)

    def render_category(self, record, value):
        Template = loader.get_template('hid/categories_column.html')
        selected = []
        for term in value:
            if term['taxonomy'] == ITEM_TYPE_CATEGORY['all']:
                selected.append(term['name'])
        ctx = {
            'categories': self.categories,
            'selected': selected,
            'record': record
        }

        return Template.render(ctx)

    def render_feedback_type(self, record, value):
        Template = loader.get_template('hid/feedback_type_column.html')

        context = self.context

        feedback_types = []
        for term in value:
            if term['taxonomy'] == 'item-types':
                feedback_types.append(term['long_name'])

        context['record'] = record
        context['feedback_types'] = ', '.join(sorted(feedback_types))

        return Template.render(context.flatten())

    def render_tags(self, record, value):
        Template = loader.get_template('hid/tags_column.html')

        context = self.context

        try:
            tags = filter(None, [
                term['name'] for term in record['terms']
                if term['taxonomy'] == 'tags'
            ])
            tags = [' '.join([x.capitalize() for x in t.split()]) for t in tags]
            context['tags'] = ', '.join(list(filter(
                lambda tag: tag != 'None' and tag is not None,
                tags
            )))
        except KeyError:
            context['tags'] = []

        context['record'] = record

        return Template.render(context.flatten())

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
