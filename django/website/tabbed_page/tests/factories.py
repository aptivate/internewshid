from factory.django import DjangoModelFactory
from factory import fuzzy

from ..models import TabbedPage, TabInstance


class TabbedPageFactory(DjangoModelFactory):
    class Meta:
        model = TabbedPage

    name = fuzzy.FuzzyText()


class TabInstanceFactory(DjangoModelFactory):
    class Meta:
        model = TabInstance

    name = fuzzy.FuzzyText()
    label = fuzzy.FuzzyText()
