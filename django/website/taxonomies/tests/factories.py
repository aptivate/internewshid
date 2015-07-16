from factory.django import DjangoModelFactory

from ..models import (
    Taxonomy,
    Term,
)


class TaxonomyFactory(DjangoModelFactory):
    class Meta:
        model = Taxonomy


class TermFactory(DjangoModelFactory):
    class Meta:
        model = Term
