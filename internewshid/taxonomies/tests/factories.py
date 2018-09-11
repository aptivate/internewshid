from factory import SubFactory, fuzzy
from factory.django import DjangoModelFactory

from ..models import Taxonomy, Term


class TaxonomyFactory(DjangoModelFactory):
    class Meta:
        model = Taxonomy
        django_get_or_create = ('name',)

    name = fuzzy.FuzzyText()


class TermFactory(DjangoModelFactory):

    class Meta:
        model = Term
        django_get_or_create = ('name', 'taxonomy')

    name = fuzzy.FuzzyText()

    taxonomy = SubFactory(TaxonomyFactory)
