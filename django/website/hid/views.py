from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic import FormView
from django.views.generic.base import TemplateView

from .forms import UploadForm, get_spreadsheet_choices


class ListSources(TemplateView):
    template_name = 'hid/sources.html'

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
    template_name = 'hid/upload.html'

    def get_success_url(self):
        return reverse("sources")

    def form_valid(self, form):
        data = form.cleaned_data
        source = data['source']
        uploaded_file = data['file']
        print source, uploaded_file

        return HttpResponseRedirect(self.get_success_url())
