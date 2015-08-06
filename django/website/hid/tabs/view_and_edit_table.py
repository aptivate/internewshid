from collections import OrderedDict
import re

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, QueryDict
from django.utils.translation import ugettext as _
from django.utils.translation import ungettext

from hid.assets import require_assets
from hid.forms import UploadForm
from hid.tables import ItemTable
import transport
from transport.exceptions import TransportException


QUESTION_TYPE_TAXONOMY = 'ebola-questions'
ADD_CATEGORY_PREFIX = 'add-category-'
DELETE_COMMAND = 'delete'
NONE_COMMAND = 'none'


class ViewAndEditTableTab(object):
    """ A table view that can be used to view messages,
        categorize them (individually and in batches)
        and delete them.

        Settings:
            label (str): Label for the table data type
            filters (dict): Filters to pass to the term
                list API
            categories (list of str): List of taxonomy slugs
                which indiciate the taxonomies the items
                in this view can be categorized by.
            columns (list of str): List of columns to display,
                from the columns available to ItemTable. If
                missing, all columns are displayed.
            per_page (int): Number of items to display per
                page. Defaults to 25.

    """
    template_name = 'hid/tabs/view_and_edit_table.html'

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

    def _get_items(self, **kwargs):
        """ Given the tab settings, return the list of items
            to include in the page

            Args:
                **kwargs (dict): Tab settings. If present
                    kwargs['filters'] is expected to be
                    a dictionary of filters that is passed
                    on to the transport API.
            Reruns:
                QuerySet: The items to list on the page
        """
        filters = kwargs.get('filters', {})
        return transport.items.list(**filters)

    def _get_columns_to_exclude(self, **kwargs):
        """ Given the tab settings, return the columns to exclude
            from the page

            Args:
                **kwargs (dict): Tab settings. If present
                    kwargs['columns'] is execpted to be a list
                    of strings listing the columns to include
            Returns:
                list of str: List of columns to exclude
        """
        included_columns = kwargs.get('columns', None)
        if included_columns is None:
            excluded_columns = ()
        else:
            all_columns = [k for k, v in ItemTable.base_columns.items()]
            excluded_columns = set(all_columns) - set(included_columns)

        return excluded_columns

    def _get_category_options(self, **kwargs):
        """ Given the tab settings, return the options to fill
            the categorisation drop down on the page.

            Args:
                **kwargs (dict): Tab settings. If present,
                   kwargs['categories'] is a list of taxonomy slugs
                   representing the taxonomies that can be used
                   to categorized the items in the table. At the
                   moment only one such taxonomy is supported.
            Returns:
                set of (value, label) pairs: The options of the
                    first categorie in categories. If no categories
                    were present, this is empty.
        """
        taxonomy_slugs = kwargs.get('categories', [])
        if len(taxonomy_slugs) > 1:
            raise Exception('ViewAndEditTableTab supports up to one category')
        if len(taxonomy_slugs) == 0:
            return ()

        terms = transport.terms.list(taxonomy=taxonomy_slugs[0])
        terms.sort(key=lambda e: e['name'].lower())
        return tuple((t['name'], t['name']) for t in terms)

    def get_context_data(self, tab_instance, request, **kwargs):
        # Build the table
        table = ItemTable(
            self._get_items(**kwargs),
            categories=self._get_category_options(**kwargs),
            exclude=self._get_columns_to_exclude(**kwargs),
            orderable=True,
            order_by=request.GET.get('sort', None),
        )
        table.paginate(
            per_page=kwargs.get('per_page', 25),
            page=request.GET.get('page', 1)
        )

        # Build the upload form
        upload_form = UploadForm(initial={'source': 'geopoll'})

        # Build the actions drop down
        actions = [
            self._build_action_dropdown_group(
                label=_('Actions'),
                items=[
                    (NONE_COMMAND, '---------'),
                    (DELETE_COMMAND, _('Delete Selected'))
                ]
            ),
            self._build_action_dropdown_group(
                label=_('Set question type'),
                items=self._get_category_options(**kwargs),
                prefix=ADD_CATEGORY_PREFIX
            )
        ]

        # Ensure we have the assets we want
        require_assets('hid/js/automatic_file_upload.js')
        require_assets('hid/js/select_all_checkbox.js')

        # And return the context
        return {
            'type_label': kwargs.get('label', '?'),
            'table': table,
            'upload_form': upload_form,
            'actions': actions,
            'next': reverse('tabbed-page', kwargs={
                'name': tab_instance.page.name,
                'tab_name': tab_instance.name
            })
        }


def _get_view_and_edit_form_request_parameters(params):
    """ Return the parameters of the given request.

    The form has mirrored inputs as the top and the
    bottom of the form. This detects which one was used
    to submit the form, and returns the parameters
    associated with that one.

    It is expected that:
        - All mirrored form elements are named as
          <name>-<placement>
        - The submit button is called 'action',
          and it's value is <action>-<placement>

    Args:
        params (QueryDict): GET or POST request parameters

    Returns:
        QueryDict: The list of invoked parameters renamed such
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


def view_and_edit_table_form_process_items(request):
    """ Request to process a selection of items from the
        view & edit table page.

        Args:
            request (Request): This should contain
                a POST request defining:
                    - action: The action to apply
                    - select_action: List of items to apply
                      the action too.
    """
    # Process the form
    if request.method == "POST":
        params = _get_view_and_edit_form_request_parameters(request.POST)
        if params['action'] == 'batchupdate':
            selected = ItemTable.get_selected(params)
            batch_action = params['batchaction']
            if batch_action == DELETE_COMMAND:
                _delete_items(request, selected)
            elif batch_action and batch_action.startswith(ADD_CATEGORY_PREFIX):
                category = batch_action[len(ADD_CATEGORY_PREFIX):]
                # TODO: add the taxonomy to the form.
                _add_items_categories(
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
            # TODO: Add the taxonomy to the form
            _add_items_categories(
                request,
                [(item, QUESTION_TYPE_TAXONOMY, category)
                 for item, category in changes]
            )
        elif params['action'] != 'none':
            messages.error(request, _('Unknown action'))

    # Find the tab to redirect to
    redirect_url = request.POST.get('next')
    if not redirect_url:
        redirect_url = reverse('data-view')
    return HttpResponseRedirect(redirect_url)


def _delete_items(request, deleted):
    """ Delete the given items, and set a success/failure
        on the request

        Args:
            request (Request): Current request object
            items (list of int): List of items to delete
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


def _add_items_categories(request, items):
    """ Add the given category to the given items,
        and set a success/failure on the request

        Args:
            request (Request): Current request object
            items (list of (item id, taxonomy_slug, term_name)):
                tupples to update.
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
