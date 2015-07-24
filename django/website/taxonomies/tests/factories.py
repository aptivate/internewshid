from factory.django import DjangoModelFactory
from factory import fuzzy, SubFactory

from ..models import (
    Taxonomy,
    Term,
)


class TaxonomyFactory(DjangoModelFactory):
    class Meta:
        model = Taxonomy
        django_get_or_create = ('name',)

    name = fuzzy.FuzzyText()


class TermFactory(DjangoModelFactory):

    class Meta:
        model = Term
        django_get_or_create = ('name',)

    name = fuzzy.FuzzyText()

    taxonomy = SubFactory(TaxonomyFactory)
