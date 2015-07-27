import re

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, QueryDict
from django.utils.translation import ugettext as _
from django.utils.translation import ungettext
from django.views.generic import FormView
from django.views.generic.base import TemplateView

from django_tables2 import SingleTableView

from chn_spreadsheet.importer import Importer, SheetImportException
from data_layer.models import Term
import transport
from transport.exceptions import TransportException
from .assets import require_assets
from .forms import UploadForm, get_spreadsheet_choices
from .tables import ItemTable


QUESTION_TYPE_TAXONOMY = 'ebola-questions'
ADD_CATEGORY_PREFIX = 'add-category-'
DELETE_COMMAND = 'delete'


class ListSources(TemplateView):
    template_name = "hid/sources.html"

    def get_sources(self):
        sources = []
        for src, label in get_spreadsheet_choices():
            sources.append({
                'name': label,
                'src': src,
                'form': UploadForm(initial={'source': src})
            })
        return sources

    def get_context_data(self, **kwargs):
        ctx = super(ListSources, self).get_context_data(**kwargs) or {}
        ctx['sources'] = self.get_sources()
        return ctx


class UploadSpreadsheetView(FormView):
    form_class = UploadForm
    template_name = "hid/upload.html"

    def get_success_url(self):
        return reverse("data-view")

    def form_valid(self, form):
        data = form.cleaned_data
        source = data['source']
        uploaded_file = data['file']

        try:
            importer = Importer()
            saved = importer.store_spreadsheet(source, uploaded_file)
            msg = ungettext("Upload successful! %d entry has been added.",
                            "Upload successful! %d entries have been added.",
                            saved) % saved

            messages.success(self.request, msg)
        except SheetImportException as exc:
            msg = exc.message
            messages.error(self.request, msg)

        return HttpResponseRedirect(self.get_success_url())


#
#  VIEW & EDIT ITEMS VIEWS
#
class ViewItems(SingleTableView):
    template_name = 'hid/view.html'
    table_class = ItemTable
    table_pagination = {
        'per_page': 25
    }

    def get_success_url(self):
        return reverse("data-view")

    def get_queryset(self):
        return transport.items.list()

    def get_category_options(self, categories_id=None):
        # TODO: Use data layer
        terms = self.get_matching_terms(categories_id)

        return tuple((t.name, t.long_name) for t in terms)

    def get_matching_terms(self, categories_id):
        if categories_id is None:
            return Term.objects.all()

        return Term.objects.filter(taxonomy__id=categories_id)

    def get_table(self, **kwargs):
        # TODO: Filter on taxonomy
        kwargs['categories'] = self.get_category_options()
        return super(ViewItems, self).get_table(**kwargs)

    def get_context_data(self, **kwargs):
        context = super(ViewItems, self).get_context_data(**kwargs)
        context['type_label'] = _('Questions')
        context['upload_form'] = UploadForm(initial={'source': 'geopoll'})
        context['actions'] = [
            self._build_action_dropdown_group(
                items=[(DELETE_COMMAND, _('Delete Selected'))]
            ),
            self._build_action_dropdown_group(
                label=_('Set question type'),
                items=self.get_category_options(),
                prefix=ADD_CATEGORY_PREFIX
            )
        ]

        require_assets('hid/js/automatic_file_upload.js')
        require_assets('hid/js/select_all_checkbox.js')
        return context

    def _build_action_dropdown_group(self, label='', items=[], prefix=''):
        """ Helper method to build a group of actions used in the
            action dropdown.

            Args:
                - label: Label of the group of action;
                - items: List of items in the group. Each item is a tupple
                         consisting of the command suffix and the display
                         name;
                - prefix: A string used to prefix the command string.

            Returns:
                A dictionary representing the action group.
        """
        return {
            'label': label,
            'items': dict(
                [(prefix + k, v) for k, v in items]
            )
        }

    @staticmethod
    def get_request_parameters(params):
        """ Return the parameters of the given request.

        The form has mirrored inputs as the top and the
        bottom of the form. This detects which one was used
        to submit the form, and returns the parameters
        associated with that one.

        It is expected that:
            - All mirrored form elements are named as
              <name>-<placement>
            - The busmit button is called 'action',
              and it's value is <action>-<placement>

        Args:
            - params: GET or POST request parameters

        Returns:
            The list of invoked parameters renamed such
            that the active parameters match the submit
            button that was invoked. If no 'action' exists
            it is defaulted to 'none' and placement to 'top'.
        """
        new_params = QueryDict('', mutable=True)
        action = params.get('action', 'none-top')
        if '-' in action:
            placement = re.sub('^[^-]+-', '', action)
            action = action[0:len(action) - len(placement) - 1]
        else:
            placement = 'top'
        for name, value in params.iterlists():
            if name == 'action':
                value = [action]
            elif name.endswith(placement):
                name = name[0:len(name)-len(placement)-1]
            new_params.setlist(name, value)
        if 'action' not in new_params:
            new_params['action'] = 'none'
        return new_params


def delete_items(request, deleted):
    """ Delete the given items, and set a success/failure
        on the request

        Args:
            - request: Current request object
            - items: List of items to delete
    """
    try:
        transport.items.bulk_delete(deleted)
        num_deleted = len(deleted)
        msg = ungettext("Successfully deleted %d item.",
                        "Successfully deleted %d items.",
                        num_deleted) % num_deleted
        messages.success(request, msg)
    except:
        msg = _("There was an error while deleting.")
        messages.error(request, msg)


def add_items_categories(request, items, category):
    """ Add the given category to the given items,
        and set a success/failure on the request

        Args:
            - request: Current request object
            - items: List of item ids to add the category too
            - category: Category name to add
    """
    success = 0
    failed = 0
    for item_id in items:
        try:
            transport.items.add_term(
                item_id,
                QUESTION_TYPE_TAXONOMY,
                category,
            )
            success += 1
        except TransportException:
            failed += 1
    if success > 0:
        msg = ungettext("Successfully updated %d item.",
                        "Successfully updated %d items.",
                        len(items)) % len(items)
        messages.success(request, msg)
    if failed > 0:
        msg = ungettext("Failed to update %d item.",
                        "Failed to update %d items.",
                        len(items)) % len(items)
        messages.success(request, msg)


def add_categories(categories):
    """ Add specified category Terms to The items
    as specified in categories list.

    args:
        categories: a list of item ids and term names:
            [ (<item-id>, <term-name>), ... ]
     """
    for item_id, term_name in categories:
        transport.items.add_term(
            item_id,
            QUESTION_TYPE_TAXONOMY,
            term_name,
        )
    # Did we want to test for any failures or exceptions ?
    # TODO: Add messages/success/error reporting here?


def process_items(request):
    """ Request to process a selection of items from the
        view & edit page.

        Args:
            - request: Request object. This should contain
              a POST request defining:
                  - action: The action to apply
                  - select_action: List of items to apply
                    the action too.
    """
    redirect_url = reverse("data-view")
    # Just redirect back to items view on GET
    if request.method == "POST":
        params = ViewItems.get_request_parameters(request.POST)
        if params['action'] == 'batchupdate':
            selected = ItemTable.get_selected(params)
            batch_action = params['batchaction']
            if batch_action == DELETE_COMMAND:
                delete_items(request, selected)
            elif batch_action and batch_action.startswith(ADD_CATEGORY_PREFIX):
                category = batch_action[len(ADD_CATEGORY_PREFIX):]
                add_items_categories(request, selected, category)
            else:
                messages.error(request, _('Unknown batch action'))
        elif params['action'] == 'save':
            changes = ItemTable.get_row_select_values(params, 'category')
            add_categories(changes)
        elif params['action'] != 'none':
            messages.error(request, _('Unknown action'))

    return HttpResponseRedirect(redirect_url)
