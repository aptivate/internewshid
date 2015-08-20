from datetime import datetime

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.views.generic.edit import FormView

import transport

from ..forms.item import AddEditItemForm
from ..constants import ITEM_TYPE_CATEGORY, DEFAULT_ITEM_TYPE


class ItemTypeNotFound(Exception):
    """ Exception raised internally when an item type is not found """
    pass


class ItemNotFound(Exception):
    """ Exception raised internally when an item is not found """
    pass


class AddEditItemView(FormView):
    template_name = "hid/add_edit_item.html"
    form_class = AddEditItemForm
    tag_fields = ('tags',)
    tag_delimiter = ','

    def _initialize_item(self, item_id, item_type):
        """ Initialize the view's item from the given item id or item_type

        This has a side effect of initializing:
            self.item_type to the item type (either from the given type
                of from the given item). If the given item has no item
                type, DEFAULT_ITEM_TYPE is assumed
            self.item to the item object (or None)
            self.item_terms to a dictionary of taxonomy to list of terms
                (or {})

        Args:
            item_id (int): Item id to initialize from
            item_type (str): Item type to initialize item_type from.
                This is used only if item_id is None.

        Raises:
            ItemNotFound: If the item was not found
            ItemTypeNotFound: If the item type was not found
        """
        self.item = None
        self.item_type = None
        self.item_terms = {}
        if item_id:
            try:
                self.item = transport.items.get(item_id)
            except transport.exceptions.TransportException:
                raise ItemNotFound()
            self.item_terms = {}
            for term in self.item['terms']:
                taxonomy = term['taxonomy']
                if taxonomy == 'item-types':
                    self.item_type = term
                if taxonomy not in self.item_terms:
                    self.item_terms[taxonomy] = []
                self.item_terms[taxonomy].append(term)
        elif item_type:
            matches = transport.terms.list(
                taxonomy='item-types',
                name=item_type
            )
            if len(matches) == 0:
                raise ItemTypeNotFound()
            else:
                self.item_type = matches[0]

        # We guarantee there is always an item type
        if self.item_type is None:
            self.item_type = DEFAULT_ITEM_TYPE

    def get(self, request, *args, **kwargs):
        """ get request handler

        If the URL defines an item_id, we load the corresponding item
        to make it available for forms.
        """
        try:
            self._initialize_item(
                kwargs.get('item_id'), kwargs.get('item_type')
            )
        except ItemNotFound:
            return self._response(
                self.request.GET.get('next', '/'),
                messages.ERROR,
                (_('Item with id %s could not be found') %
                 str(kwargs.get('item_id')))
            )
        except ItemTypeNotFound:
            return self._response(
                self.request.GET.get('next', '/'),
                messages.ERROR,
                (_('Item type %s could not be found') %
                 str(kwargs.get('item_type')))
            )
        return super(AddEditItemView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """ post request handler

        If the URL defines an item_id, we load the corresponding item
        to make it available for forms.

        We handle cancel and delete here, as the form doesn't need to be
        valid for those.
        """
        try:
            self._initialize_item(
                kwargs.get('item_id'), kwargs.get('item_type')
            )
        except ItemNotFound:
            return self._response(
                self.request.GET.get('next', '/'),
                messages.ERROR,
                (_('Item with id %s could not be found') %
                 str(kwargs.get('item_id')))
            )
        except ItemTypeNotFound:
            return self._response(
                self.request.GET.get('next', '/'),
                messages.ERROR,
                (_('Item type %s could not be found') %
                 str(kwargs.get('item_type')))
            )

        if 'cancel' in self.request.POST['action']:
            return self._response(
                self.request.POST['next'],
                messages.INFO,
                _('No action performed')
            )
        if 'delete' in self.request.POST['action']:
            return self._delete_item()

        return super(AddEditItemView, self).post(request, *args, **kwargs)

    def get_initial(self):
        """ Return the form object's initial values for the current item """
        if self.item is None:
            initial = {
                'id': 0,
                'timestamp': datetime.now(),
                'next': self.request.GET.get('next', self.request.path)
            }
        else:
            initial = {
                'id': self.item['id'],
                'body': self.item['body'],
                'timestamp': self.item['timestamp'],
                'next': self.request.GET.get(
                    'next',
                    self.request.META.get('HTTP_REFERER', reverse('dashboard'))),

            }

        taxonomy = ITEM_TYPE_CATEGORY.get(self.item_type['name'])
        if (taxonomy and taxonomy in self.item_terms
                and len(self.item_terms[taxonomy]) > 0):
            initial['category'] = self.item_terms[taxonomy][0]['name']

        for taxonomy, terms in self.item_terms.iteritems():
            if taxonomy in self.tag_fields:
                term_names = [t['name'] for t in terms]
                initial[taxonomy] = self.tag_delimiter.join(term_names)

        return initial

    def get_form(self, form_class):
        """ Return the form object to be used """
        return form_class(self.item_type['name'], **self.get_form_kwargs())

    def get_context_data(self, **kwargs):
        """ Get the form's context data

        We invoke FormView's get_context_data and add the current
        item.
        """
        context = super(AddEditItemView, self).get_context_data(**kwargs)

        # Add item and form mode to the context
        context['item'] = self.item
        context['update'] = self.item is not None

        # Add the type label to the context
        context['item_type_label'] = self.item_type['long_name']

        # Add the width of the option row to the context
        option_row_widget_count = 1  # We always have 'created'
        if 'category' in kwargs['form'].fields:
            option_row_widget_count += 1
        if 'region' in kwargs['form'].fields:
            option_row_widget_count += 1
        context['option_row_width'] = 12 / option_row_widget_count

        return context

    def form_valid(self, form):
        """ Form submit handler """
        item_description = self._get_item_description()
        taxonomy = ITEM_TYPE_CATEGORY.get(self.item_type['name'])
        item_id = int(form.cleaned_data['id'])

        try:
            if item_id == 0:
                self.item = self._create_item(form, taxonomy)
                message = _("%s %d successfully created.") % (
                    item_description,
                    self.item['id']
                )
                message_code = messages.SUCCESS
            else:
                self._update_item(
                    item_id, form, taxonomy
                )
                message = _("%s %d successfully updated.") % (
                    item_description,
                    item_id,
                )
                message_code = messages.SUCCESS
        except transport.exceptions.TransportException as e:
            message = e.message.get('detail')
            if message is None:
                message = e.message

            message_code = messages.ERROR

        return self._response(
            form.cleaned_data['next'],
            message_code,
            message)

    def _separate_form_data(self, form):
        data = dict(form.cleaned_data)
        category = data.pop('category', None)
        data.pop('id', None)

        tags = {}
        regular_fields = {}

        for (field_name, field_value) in data.iteritems():
            if field_name in self.tag_fields:
                tags[field_name] = field_value
            else:
                regular_fields[field_name] = field_value

        return category, tags, regular_fields

    def _add_tags(self, item_id, tags):
        for (taxonomy, value) in tags.iteritems():
            transport.items.delete_all_terms(item_id, taxonomy)
            term_names = [t.strip() for t in value.split(self.tag_delimiter)]

            transport.items.add_terms(item_id, taxonomy, term_names)

    def _update_item(self, item_id, form, taxonomy):
        """ Update the given item

            Args:
                item_id (int): Item id to update
                form (Form): Valid form object containing fields
                taxonomy (str or None): Taxonomy of the item's
                    category field, if any

            Raises:
                TransportException: On API errors
        """

        category, tags, regular_fields = self._separate_form_data(
            form)

        transport.items.update(item_id, regular_fields)

        # TODO: Combine terms into single transaction
        if taxonomy:
            if category:
                transport.items.add_terms(item_id, taxonomy, category)
            else:
                transport.items.delete_all_terms(item_id, taxonomy)

        self._add_tags(item_id, tags)

    def _create_item(self, form, taxonomy):
        """ Create the given item

            Args:
                item_id (int): Item id to update
                form (Form): Valid form object containing fields
                taxonomy (str or None): Taxonomy of the item's
                    category field, if any

            Returns:
                dict: The created item

            Raises:
                TransportException: On API errors
        """
        category, tags, regular_fields = self._separate_form_data(
            form)

        created_item = transport.items.create(regular_fields)

        # TODO: Combine terms into single transaction
        transport.items.add_terms(
            created_item['id'], 'item-types', self.item_type['name']
        )
        if taxonomy and category:
            transport.items.add_terms(created_item['id'], taxonomy, category)

        self._add_tags(created_item['id'], tags)

        return created_item

    def form_invalid(self, form):
        """ Form invalid handler """
        messages.add_message(
            self.request,
            messages.ERROR,
            _("The form could not be submitted."
              "Please correct the errors and submit it again.")
        )
        return super(AddEditItemView, self).form_invalid(form)

    def _response(self, url, message_type, message):
        """ Log a message and return an HTTP Response

        Args:
            url (str): URL to redirect to
            message_type (str): Message type to log (from message.INFO, etc.)
            message (str): Message to log
        Returns:
            HttpResponseRedirect: Response object
        """
        messages.add_message(self.request, message_type, message)
        return HttpResponseRedirect(url)

    def _delete_item(self):
        id = self.item['id']
        transport.items.delete(id)

        item_description = self._get_item_description()

        return self._response(
            self._get_next_url_for_delete(),
            messages.SUCCESS,
            _("%s %d successfully deleted.") % (
                item_description,
                id,
            )
        )

    def _get_next_url_for_delete(self):
        next_url = self.request.POST.get('next', reverse('dashboard'))

        return next_url

    def _get_item_description(self):
        return self.item_type['long_name']
