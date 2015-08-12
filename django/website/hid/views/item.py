from django.views.generic.base import TemplateView


class AddEditItem(TemplateView):
    template_name = "hid/item.html"

    def get_context_data(self, **kwargs):
        ctx = super(AddEditItem, self).get_context_data(**kwargs) or {}
        return ctx
