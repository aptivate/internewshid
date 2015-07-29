import re

from collections import OrderedDict

from django.contrib import messages
from django.contrib.auth.views import login
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, QueryDict
from django.utils.translation import ugettext as _
from django.utils.translation import ungettext
from django.views.generic import FormView
from django.views.generic.base import TemplateView

from django_tables2 import SingleTableView

from chn_spreadsheet.importer import Importer, SheetImportException
import transport
from transport.exceptions import TransportException
from .assets import require_assets
from .forms import UploadForm, get_spreadsheet_choices
from .tables import ItemTable


QUESTION_TYPE_TAXONOMY = 'ebola-questions'
ADD_CATEGORY_PREFIX = 'add-category-'
DELETE_COMMAND = 'delete'
NONE_COMMAND = 'none'


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

    def get_category_options(self, taxonomy_slug=None):
        if taxonomy_slug is not None:
            terms = transport.terms.list(taxonomy=taxonomy_slug)
        else:
            terms = transport.terms.list()
        terms.sort(key=lambda e: e['name'].lower())
        return tuple((t['name'], t['name']) for t in terms)

    def get_table(self, **kwargs):
        kwargs['categories'] = self.get_category_options(
            QUESTION_TYPE_TAXONOMY
        )
        return super(ViewItems, self).get_table(**kwargs)

    def get_context_data(self, **kwargs):
        context = super(ViewItems, self).get_context_data(**kwargs)
        context['type_label'] = _('Questions')
        context['upload_form'] = UploadForm(initial={'source': 'geopoll'})
        context['actions'] = [
            self._build_action_dropdown_group(
                label=_('Actions'),
                items=[
                    (NONE_COMMAND, '---------'),
                    (DELETE_COMMAND, _('Delete Selected'))
                ]
            ),
            self._build_action_dropdown_group(
                label=_('Set question type'),
                items=self.get_category_options(QUESTION_TYPE_TAXONOMY),
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
            'items': OrderedDict(
                [(prefix + entry_cmd, entry_label)
                    for entry_cmd, entry_label in items]
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


class ViewSingleItem(TemplateView):
    template_name = "hid/item.html"

    def get_context_data(self, **kwargs):
        ctx = super(ViewSingleItem, self).get_context_data(**kwargs) or {}
        return ctx


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
        msg = ungettext("%d item deleted.",
                        "%d items deleted.",
                        num_deleted) % num_deleted
        messages.success(request, msg)
    except:
        msg = _("There was an error while deleting.")
        messages.error(request, msg)


def add_items_categories(request, items):
    """ Add the given category to the given items,
        and set a success/failure on the request

        Args:
            - request: Current request object
            - items: List of (item id, taxonomy_slug, term_name) tupples to
                     update.
    """
    success = 0
    failed = 0
    for item_id, taxonomy_slug, term_name in items:
        try:
            transport.items.add_term(
                item_id,
                taxonomy_slug,
                term_name
            )
            success += 1
        except TransportException:
            failed += 1
    if success > 0:
        msg = ungettext("Updated %d item.",
                        "Updated %d items.",
                        len(items)) % len(items)
        messages.success(request, msg)
    if failed > 0:
        msg = ungettext("Failed to update %d item.",
                        "Failed to update %d items.",
                        len(items)) % len(items)
        messages.success(request, msg)


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
                add_items_categories(
                    request,
                    [(item, QUESTION_TYPE_TAXONOMY, category)
                     for item in selected]
                )
            elif batch_action == NONE_COMMAND:
                pass
            else:
                messages.error(request, _('Unknown batch action'))
        elif params['action'] == 'save':
            changes = ItemTable.get_row_select_values(params, 'category')
            add_items_categories(
                request,
                [(item, QUESTION_TYPE_TAXONOMY, category)
                 for item, category in changes]
            )
        elif params['action'] != 'none':
            messages.error(request, _('Unknown action'))

    return HttpResponseRedirect(redirect_url)


def csrf_failure(request, reason=''):
    # If the user presses the back button in the browser to go back to the
    # login page and logs in again, they will get a CSRF error page because
    # the token will be wrong.
    # We override this with a redirect to the dashboard, which if not already
    # logged in, will redirect to the login page (with a fresh token).

    return HttpResponseRedirect(reverse('dashboard'))
