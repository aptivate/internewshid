from datetime import datetime

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import ugettext as _
from django.views.generic.edit import FormView

import transport

from ..constants import DEFAULT_ITEM_TYPE, ITEM_TYPE_CATEGORY
from ..forms.item import AddEditItemForm


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

        # TODO remove singular item_type once we've got multiple working
        self.item_type = []

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
                    self.item_type.append(term)
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
                self.item_type = [matches[0]]

        # We guarantee there is always an item type
        if not self.item_type:
            self.item_type = [DEFAULT_ITEM_TYPE]
            if 'item-types' not in self.item_terms:
                self.item_terms['item-types'] = []
            self.item_terms['item-types'].append(DEFAULT_ITEM_TYPE)

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
                (_('Item with id {0} could not be found').format(
                 str(kwargs.get('item_id'))))
            )
        except ItemTypeNotFound:
            return self._response(
                self.request.GET.get('next', '/'),
                messages.ERROR,
                (_('Item type {0} could not be found').format(
                 str(kwargs.get('item_type'))))
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
                kwargs.get('item_id'),
                kwargs.get('item_type')
            )
        except ItemNotFound:
            return self._response(
                self.request.GET.get('next', '/'),
                messages.ERROR,
                (_('Item with id {0} could not be found').format(
                 str(kwargs.get('item_id'))))
            )
        except ItemTypeNotFound:
            return self._response(
                self.request.GET.get('next', '/'),
                messages.ERROR,
                (_('Item type {0} could not be found').format(
                 str(kwargs.get('item_type'))))
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
                'translation': self.item.get('translation', ''),
                'location': self.item.get('location', ''),
                'sub_location': self.item.get('sub_location', ''),
                'language': self.item.get('language', ''),
                'risk': self.item.get('risk', ''),
                'gender': self.item.get('gender', ''),
                'contributor': self.item.get('contributor', ''),
                'collection_type': self.item.get('collection_type', ''),
                'timestamp': self.item['timestamp'],
                'next': self.request.GET.get(
                    'next',
                    self.request.META.get(
                        'HTTP_REFERER',
                        reverse('dashboard')
                    )
                ),
            }

        taxonomy = ITEM_TYPE_CATEGORY.get('all')
        if (taxonomy and taxonomy in self.item_terms
                and len(self.item_terms[taxonomy]) > 0):
            initial['category'] = self.item_terms[taxonomy][0]['name']

        for taxonomy, terms in self.item_terms.items():
            if taxonomy in self.tag_fields:
                term_names = [t['name'] for t in terms]
                initial[taxonomy] = self.tag_delimiter.join(term_names)

        if 'item-types' in self.item_terms:
            # TODO when multiple types are fully supported delete the single feedback_type
            initial['feedback_type'] = self.item_terms['item-types'][0]['name']

            terms = self.item_terms['item-types']
            feedback_names = [t['name'] for t in terms]
            initial['feedback_type'] = feedback_names

        if 'age-ranges' in self.item_terms:
            initial['age_range'] = self.item_terms['age-ranges'][0]['name']

        return initial

    def get_form(self, form_class=None):
        """ Return the form object to be used """
        if form_class is None:
            form_class = self.form_class

        kwargs = self.get_form_kwargs()

        kwargs['feedback_disabled'] = self._feedback_disabled()

        return form_class(**kwargs)

    def _feedback_disabled(self):
        if not hasattr(self.request, 'user'):
            # only when testing?
            return False

        if self.request.user.has_perm('data_layer.can_change_message_body'):
            return False

        return True

    def get_context_data(self, **kwargs):
        """ Get the form's context data

        We invoke FormView's get_context_data and add the current
        item.
        """
        context = super(AddEditItemView, self).get_context_data(**kwargs)

        # Add item and form mode to the context
        context['item'] = self.item
        # Stashing values in the context because of a naming clash with a method on self.item
        # prevent us from referencing values directly in the template
        if self.item:
            context['keyvalues'] = self.item.get('values')
        context['update'] = self.item is not None

        # Add the type label to the context
        # This isn't currently used in any templates so just returning the first item type.
        context['item_type_label'] = self.item_type[0]['long_name']

        # Add the width of the option row to the context
        option_row_widget_count = 1  # We always have 'created'
        if 'category' in context['form'].fields:
            option_row_widget_count += 1
        if 'region' in context['form'].fields:
            option_row_widget_count += 1
        context['option_row_width'] = 12 / option_row_widget_count

        return context

    def form_valid(self, form):
        """ Form submit handler """
        taxonomy = ITEM_TYPE_CATEGORY.get('all')
        item_id = int(form.cleaned_data['id'])

        try:
            if item_id == 0:
                self.item = self._create_item(form, taxonomy)
                item_description = self._get_item_description()
                message = _("{0} {1} successfully created.").format(
                    item_description,
                    self.item['id']
                )
                message_code = messages.SUCCESS
            else:
                self._update_item(item_id, form)
                item_description = self._get_item_description()
                message = _("{0} {1} successfully updated.").format(
                    item_description,
                    item_id,
                )
                message_code = messages.SUCCESS
        except transport.exceptions.ItemNotUniqueException as e:
            message = _("This record could not be saved because the body and "
                        "timestamp clashed with an existing record")
            message_code = messages.ERROR

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
        feedback_type = data.pop('feedback_type', None)
        age_range = data.pop('age_range', None)
        data.pop('id', None)

        tags = {}
        regular_fields = {}

        for (field_name, field_value) in data.items():
            if field_name in self.tag_fields:
                tags[field_name] = field_value
            else:
                regular_fields[field_name] = field_value

        return category, tags, feedback_type, age_range, regular_fields

    def _add_tags(self, item_id, tags):
        for (taxonomy, value) in tags.items():
            transport.items.delete_all_terms(item_id, taxonomy)
            term_names = [t.strip() for t in value.split(self.tag_delimiter)]

            transport.items.add_terms(item_id, taxonomy, term_names)

    def _add_feedback(self, item_id, feedback):
        pass

    def _update_item(self, item_id, form):
        """ Update the given item

            Args:
                item_id (int): Item id to update
                form (Form): Valid form object containing fields
                taxonomy (str or None): Taxonomy of the item's
                    category field, if any

            Raises:
                TransportException: On API errors
        """

        (category, tags, feedback_type, age_range,
         regular_fields) = self._separate_form_data(form)

        transport.items.update(item_id, regular_fields)

        # TODO: Combine terms into single transaction
        category_taxonomy = ITEM_TYPE_CATEGORY.get('all')

        if category:
            transport.items.add_terms(item_id, category_taxonomy, category)
        else:
            transport.items.delete_all_terms(item_id, category_taxonomy)

        # TODO this should be removed once we get updating working for multiple feedback types
        if feedback_type:
            transport.items.delete_all_terms(item_id, 'item-types')
            self.item_type = []
            for feedback_type_item in feedback_type:
                item = transport.items.add_terms(item_id, 'item-types', feedback_type_item)
                self.item_type.append(self._get_item_type_term(item))
        else:
            transport.items.delete_all_terms(item_id, 'item-types')

        if age_range:
            transport.items.add_terms(item_id, 'age-ranges', age_range)
        else:
            transport.items.delete_all_terms(item_id, 'age-ranges')

        self._add_feedback(item_id, feedback_type)
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
        (category, tags, feedback_type, age_range,
         regular_fields) = self._separate_form_data(form)

        if not feedback_type:
            feedback_type = [self.item_type[0]['name']]

        created_item = transport.items.create(regular_fields)

        # TODO: Combine terms into single transaction
        # TODO: Don't set this here - handle more generically as hidden form
        # parameter
        transport.items.add_terms(
            created_item['id'], 'data-origins', 'Form Entry',
        )
        for feedback_type_item in feedback_type:
            self.item_type = []
            updated_item = transport.items.add_terms(
                created_item['id'], 'item-types', feedback_type_item
            )
            self.item_type.append(self._get_item_type_term(updated_item))

        if taxonomy and category:
            transport.items.add_terms(created_item['id'], taxonomy, category)

        if age_range:
            transport.items.add_terms(created_item['id'], 'age-ranges',
                                      age_range)

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
            _("{0} {1} successfully deleted.").format(
                item_description,
                id,
            )
        )

    def _get_next_url_for_delete(self):
        next_url = self.request.POST.get('next', reverse('dashboard'))

        return next_url

    def _get_item_description(self):
        return ','.join([x['long_name'] for x in self.item_type])

    # TODO should probably change this to supporting multiple types directly.
    def _get_item_type_term(self, item):
        for term in item['terms']:
            if term['taxonomy'] == 'item-types':
                return term

        return self.item_type[0]
