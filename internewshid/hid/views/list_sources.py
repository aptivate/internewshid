from django.views.generic.base import TemplateView

from ..forms.upload import UploadForm, get_spreadsheet_choices


class ListSources(TemplateView):
    template_name = "hid/sources.html"

    def get_sources(self):
        sources = []
        for source, label in get_spreadsheet_choices():
            sources.append({
                'name': label,
                'src': source,
                'form': UploadForm(initial={'source': source})
            })
        return sources

    def get_context_data(self, **kwargs):
        ctx = super(ListSources, self).get_context_data(**kwargs) or {}
        ctx['sources'] = self.get_sources()
        return ctx
