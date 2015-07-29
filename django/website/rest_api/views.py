from django.db.models import Count
from django.utils.translation import ugettext as _

from rest_framework import viewsets, status
from rest_framework_bulk.mixins import BulkDestroyModelMixin
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from data_layer.models import (
    Item,
)

from taxonomies.models import (
    Taxonomy,
    Term,
)

from .serializers import (
    ItemSerializer,
    TaxonomySerializer,
    TermSerializer,
    TermItemCountSerializer,
)


class ItemViewSet(viewsets.ModelViewSet, BulkDestroyModelMixin):
    serializer_class = ItemSerializer
    filter_fields = ('created', 'body', 'timestamp', )

    def get_queryset(self):
        items = Item.objects.all()
        ids = self.request.query_params.getlist('ids')
        if ids:
            items = items.filter(id__in=ids)

        return items

    @detail_route(methods=['post'])
    def add_term(self, request, item_pk):
        item = Item.objects.get(pk=item_pk)
        term_data = request.data
        try:
            term = Term.objects.by_taxonomy(
                taxonomy=term_data['taxonomy'],
                name=term_data['name'],
            )
        except Term.DoesNotExist as e:
            data = {'detail': e.message}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        item.apply_term(term)
        data = {}  # TODO should be the item containing the new term
        return Response(data, status=status.HTTP_200_OK)


class TaxonomyViewSet(viewsets.ModelViewSet):
    serializer_class = TaxonomySerializer

    queryset = Taxonomy.objects.all()

    lookup_field = 'slug'

    @detail_route(methods=['get'])
    def itemcount(self, request, slug):
        try:
            taxonomy = Taxonomy.objects.get(slug=slug)
        except Taxonomy.DoesNotExist:
            message = _("Taxonomy with slug '%s' does not exist.") % (slug)

            data = {'detail': message}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        terms = self._get_terms(request, taxonomy)

        data = TermItemCountSerializer(terms, many=True).data

        return Response(data, status=status.HTTP_200_OK)

    def _get_terms(self, request, taxonomy):
        start_time = request.query_params.get('start_time', None)
        end_time = request.query_params.get('end_time', None)

        filters = {'taxonomy': taxonomy}

        if start_time is not None and end_time is not None:
            filters['items__timestamp__range'] = [start_time, end_time]

        return Term.objects.filter(**filters).annotate(
            count=Count('items'))


class TermViewSet(viewsets.ModelViewSet):
    serializer_class = TermSerializer

    queryset = Term.objects.all()

    def get_queryset(self):
        """ Return the query set to fetch terms.

        The request may contain the following
        exact match filters:
            name: Name of the term
            long_name: Long name of the term
            taxonomy: Slug of the term's taxonomy

        Returns:
            QuerySet: A query set
        """
        items = Term.objects.all()

        name = self.request.query_params.get('name', None)
        if name is not None:
            items = items.filter(name=name)

        long_name = self.request.query_params.get('long_name', None)
        if long_name is not None:
            items = items.filter(long_name=long_name)

        taxonomy_slug = self.request.query_params.get('taxonomy', None)
        if taxonomy_slug is not None:
            items = items.filter(taxonomy__slug=taxonomy_slug)

        return items
