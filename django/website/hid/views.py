from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.utils.translation import ungettext
from django.views.generic import FormView
from django.views.generic.base import TemplateView

from django_tables2 import SingleTableView

from chn_spreadsheet.importer import Importer, SheetImportException
import transport
from .forms import UploadForm, get_spreadsheet_choices
from .tables import ItemTable


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
        return transport.get_items()

    def get_category_options(self, categories_id=None):
        '''
        TODO: Fetch categories based on their id
        '''
        return (
            ('first', 'First'),
            ('second', 'Second option with a long name'),
            ('third', 'Third'),
            ('fourth', 'Fourth'),
        )

    def get_table(self, **kwargs):
        kwargs['categories'] = self.get_category_options()
        return super(ViewItems, self).get_table(**kwargs)


def get_deleted(params):
    return [int(x) for x in params.getlist("delete", [])]


def get_categories(params, deleted_ids=[]):
    removed = set(deleted_ids)
    cat_id = lambda x: int(x[9:])
    is_cat = lambda x: x.startswith("category-")

    categories = [(cat_id(key), val) for key, val in params.items() if is_cat(key)]
    return [cat for cat in categories if cat[0] not in removed]


def delete_items(request, deleted):
    try:
        transport.delete_items(deleted)
        num_deleted = len(deleted)
        msg = ungettext("Successfully deleted %d item.",
                        "Successfully deleted %d items.",
                        num_deleted) % num_deleted
        messages.success(request, msg)
    except:
        msg = _("There was an error while deleting.")
        messages.error(request, msg)


def process_items(request):
    '''
    If POST request, then:
    - delete items that were checked
    - update categories on those that weren't deleted.
    '''
    redirect_url = reverse("data-view")
    # Just redirect back to items view on GET
    if request.method == "POST":
        deleted = get_deleted(request.POST)
        categories = get_categories(request.POST, deleted)
        if len(deleted):
            delete_items(request, deleted)
        if len(categories):
            # Update categories as well
            pass

    return HttpResponseRedirect(redirect_url)
