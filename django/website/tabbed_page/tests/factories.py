from factory.django import DjangoModelFactory
from factory import fuzzy

from ..models import TabbedPage


class TabbedPageFactory(DjangoModelFactory):
    class Meta:
        model = TabbedPage

    name = fuzzy.FuzzyText()
