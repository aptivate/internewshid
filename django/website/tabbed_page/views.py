from django.views.generic import TemplateView

from .models import TabbedPage


class TabbedPageView(TemplateView):
    template_name = "tabbed_page/tabbed_page.html"
    _page = None

    @property
    def tabs(self):
        return self.page.tab_set.all().order_by('position')

    @property
    def page(self):
        if self._page is None:
            name = self.kwargs.get('name')

            # TODO: check if name can ever be empty string
            # if not, can just put default in get() above
            if not name:
                name = 'main'

            self._page = TabbedPage.objects.get(name=name)

        return self._page
