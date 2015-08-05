from factory.django import DjangoModelFactory
from factory import fuzzy

from ..models import TabbedPage, Tab


class TabbedPageFactory(DjangoModelFactory):
    class Meta:
        model = TabbedPage

    name = fuzzy.FuzzyText()


class TabFactory(DjangoModelFactory):
    class Meta:
        model = Tab

    name = fuzzy.FuzzyText()
    label = fuzzy.FuzzyText()
