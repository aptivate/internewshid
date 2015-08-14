from django.contrib import messages
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.views.generic.edit import FormView

import transport
from ..forms.item import AddEditItemForm
from ..constants import ITEM_TYPE_CATEGORY


class AddEditItemView(FormView):
    template_name = "hid/add_edit_item.html"
    form_class = AddEditItemForm

    def _initialize_item(self, item_id):
        """ Initialize the view's item from the given item id.

        This has a side effect of initializing:
            self.item to the item object (or None)
            self.item_type to the item type, if defined (None otherwise)
            self.item_terms to a dictionary of taxonomy to list of terms

        Args:
            item_id (int): Item id
        """
        self.item = None
        self.item_type = None
        self.item_terms = None
        if not item_id:
            return
        self.item = transport.items.get(item_id)
        self.item_terms = {}
        for term in self.item['terms']:
            taxonomy = term['taxonomy']
            if taxonomy == 'item-types':
                self.item_type = term
            if taxonomy not in self.item_terms:
                self.item_terms[taxonomy] = []
            self.item_terms[taxonomy].append(term)

    def get(self, request, *args, **kwargs):
        """ get request handler

        If the URL defines an item_id, we load the corresponding item
        to make it available for forms.
        """
        try:
            self._initialize_item(kwargs.get('item_id'))
        except transport.exceptions.TransportException:
            return self._response(
                self.request.GET.get('next', '/'),
                messages.ERROR,
                (_('Item with id %s could not be found') %
                 str(kwargs.get('item_id')))
            )
        return super(AddEditItemView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """ post request handler

        If the URL defines an item_id, we load the corresponding item
        to make it available for forms.

        We handle cancel and delete here, as the form doesn't it to be
        valid for those.
        """
        try:
            self._initialize_item(kwargs.get('item_id'))
        except transport.exceptions.TransportException:
            return self._response(
                self.request.GET.get('next', '/'),
                messages.ERROR,
                (_('Item with id %s could not be found') %
                 str(kwargs.get('item_id')))
            )

        if 'cancel' in self.request.POST['action']:
            return self._response(
                self.request.POST['next'],
                messages.INFO,
                _('No action performed')
            )
        if 'delete' in self.request.POST['action']:
            return self._response(
                self.request.POST['next'],
                messages.ERROR,
                _('Delete item not implemented')
            )

        return super(AddEditItemView, self).post(request, *args, **kwargs)

    def get_initial(self):
        """ Return the form object's initial values for the current item """
        if self.item is None:
            return {
                'id': 0
            }
        initial = {
            'id': self.item['id'],
            'body': self.item['body'],
            'timestamp': self.item['timestamp'],
            'next': self.request.GET.get('next', self.request.path)
        }
        taxonomy = ITEM_TYPE_CATEGORY.get(self.item_type['name'])
        if (taxonomy and taxonomy in self.item_terms
                and len(self.item_terms[taxonomy]) > 0):
            initial['category'] = self.item_terms[taxonomy][0]['name']

        return initial

    def get_form(self, form_class):
        """ Return the form object to be used """
        if self.item_type:
            item_type = self.item_type['name']
        else:
            # TODO: When implementing ADD mode, we'll need to use the URL to
            # get the default
            item_type = None
        return form_class(item_type, **self.get_form_kwargs())

    def get_context_data(self, **kwargs):
        """ Get the form's context data

        We invoke FormView's get_context_data and add the current
        item.
        """
        context = super(AddEditItemView, self).get_context_data(**kwargs)

        # Add item to the context
        context['item'] = self.item

        # Add the type label to the context
        # TODO: When implementing ADD mode, we'll need to use the URL to
        # get the default.
        context['item_type_label'] = '?'
        if self.item_type:
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
        # if self.item_type:
        #     item_type = self.item_type['long_name']
        # else:
        #     item_type = 'Item'
        # msg = _("%s %d successfully updated.") % (
        #     item_type,
        #     int(form.cleaned_data['id'])
        # )

        # return self._response(
        #    form.cleaned_data['next'],
        #    messages.SUCCESS,
        #    msg
        # )
        return self._response(
            form.cleaned_data['next'],
            messages.ERROR,
            _('Update item not implemented')
        )

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
