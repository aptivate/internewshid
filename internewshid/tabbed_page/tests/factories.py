from factory import fuzzy
from factory.django import DjangoModelFactory

from ..models import TabbedPage, TabInstance


class TabbedPageFactory(DjangoModelFactory):
    class Meta:
        model = TabbedPage
        django_get_or_create = ('name',)

    name = fuzzy.FuzzyText()


class TabInstanceFactory(DjangoModelFactory):
    class Meta:
        model = TabInstance
        django_get_or_create = ('name',)

    name = fuzzy.FuzzyText()
    label = fuzzy.FuzzyText()
