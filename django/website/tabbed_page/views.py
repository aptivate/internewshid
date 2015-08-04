from django.views.generic import TemplateView

from .models import TabbedPage


class TabbedPageView(TemplateView):
    template_name = "tabbed_page/tabbed_page.html"

    @property
    def page_name(self):
        name = self.kwargs.get('name')

        if name:
            page = TabbedPage.objects.get(name=name)
            return page.name

        return 'main'
