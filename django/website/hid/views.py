from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import ungettext
from django.views.generic import FormView
from django.views.generic.base import TemplateView

from chn_spreadsheet.importer import Importer, SheetImportException
from .forms import UploadForm, get_spreadsheet_choices


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
        return reverse("tabbed-page", name="main", tab_name="all")

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


class ViewSingleItem(TemplateView):
    template_name = "hid/item.html"

    def get_context_data(self, **kwargs):
        ctx = super(ViewSingleItem, self).get_context_data(**kwargs) or {}
        return ctx


def csrf_failure(request, reason=''):
    # If the user presses the back button in the browser to go back to the
    # login page and logs in again, they will get a CSRF error page because
    # the token will be wrong.
    # We override this with a redirect to the dashboard, which if not already
    # logged in, will redirect to the login page (with a fresh token).

    return HttpResponseRedirect(reverse('dashboard'))
