from django.views.generic.base import TemplateView

from ..forms.upload import UploadForm, get_spreadsheet_choices


class ListCollectionTypes(TemplateView):
    template_name = "hid/collection_types.html"

    def get_collection_types(self):
        collection_types = []
        for collection_type, label in get_spreadsheet_choices():
            collection_types.append({
                'name': label,
                'src': collection_type,
                'form': UploadForm(initial={'collection_type': collection_type})
            })
        return collection_types

    def get_context_data(self, **kwargs):
        ctx = super(ListCollectionTypes, self).get_context_data(**kwargs) or {}
        ctx['collection_types'] = self.get_collection_types()
        return ctx
