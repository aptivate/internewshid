from factory.django import DjangoModelFactory

from ..models import Taxonomy


class TaxonomyFactory(DjangoModelFactory):

    class Meta:
        model = Taxonomy
