from factory import Sequence, SubFactory, fuzzy
from factory.django import DjangoModelFactory

from ..models import Taxonomy, Term


class TaxonomyFactory(DjangoModelFactory):
    class Meta:
        model = Taxonomy
        django_get_or_create = ('name', 'slug')

    name = Sequence(lambda n: 'Name {}'.format(n))
    slug = Sequence(lambda n: 'name-{}'.format(n))


class TermFactory(DjangoModelFactory):

    class Meta:
        model = Term
        django_get_or_create = ('name', 'taxonomy')

    name = fuzzy.FuzzyText()

    taxonomy = SubFactory(TaxonomyFactory)
