from django.views.generic import TemplateView

from .models import TabbedPage


class TabbedPageView(TemplateView):
    template_name = "tabbed_page/tabbed_page.html"
    _page = None
    _active_tab = None

    @property
    def tabs(self):
        return self.page.tabs.all().order_by('position')

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

    @property
    def active_tab(self):
        if self._active_tab is None:
            candidates = []
            tab_name = self.kwargs.get('tab_name')
            if tab_name:
                candidates = self.page.tabs.all().filter(name=tab_name)
            if len(candidates) == 0:
                candidates = self.page.tabs.all().filter(default=True)
            if len(candidates) == 0:
                candidates = self.page.tabs.all()
            if len(candidates) > 0:
                self._active_tab = candidates[0]
        return self._active_tab
