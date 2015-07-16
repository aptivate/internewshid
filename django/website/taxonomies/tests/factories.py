from factory.django import DjangoModelFactory
from factory import fuzzy, SubFactory

from ..models import Term, Taxonomy


class TaxonmyFactory(DjangoModelFactory):

    class Meta:
        model = Taxonomy

    name = fuzzy.FuzzyText()


class TermFactory(DjangoModelFactory):

    class Meta:
        model = Term

    name = fuzzy.FuzzyText()

    taxonomy = SubFactory(TaxonmyFactory)
