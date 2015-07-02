from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.utils.translation import ungettext
from django.views.generic import FormView
from django.views.generic.base import TemplateView

from django_tables2 import SingleTableView

from chn_spreadsheet.utils import store_spreadsheet, SheetImportException
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
            saved = store_spreadsheet(source, uploaded_file)
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


def get_deleted(params):
    return [int(x) for x in params.getlist("delete", [])]


def process_items(request):
    redirect_url = reverse("data-view")
    if request.method == "POST":
        deleted = get_deleted(request.POST)
        if len(deleted):
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

    return HttpResponseRedirect(redirect_url)
