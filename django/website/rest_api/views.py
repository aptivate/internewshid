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
        """ Return the queryset for this view.

        This accepts two get parameters for filtering:
            ids: A list of ids
            terms: A list of strings formatted as
                <taxonomy slug>:<term name>.

                Notes:

                - Only items that have all the given
                  terms are returned;
                - taxonomy slugs do not allow ':'
                  characters, so no escaping is
                  needed.

        Returns:
            QuerySet: The filtered list of items
        """
        items = Item.objects.prefetch_related('terms', 'terms__taxonomy').all()

        # Filter on ids
        ids = self.request.query_params.getlist('ids')
        if ids:
            items = items.filter(id__in=ids)

        # Filter on terms
        terms = self.request.query_params.getlist('terms', [])
        for taxonomy_and_term in terms:
            (taxonomy, term) = taxonomy_and_term.split(':', 1)
            matches = Term.objects.filter(
                name=term, taxonomy__slug=taxonomy
            )
            if len(matches) == 0:
                # If the term doesn't exist, there can be no matches
                return Item.objects.none()

            items = items.filter(terms__id=matches[0].id)

        return items

    @detail_route(methods=['post'])
    def add_terms(self, request, item_pk):
        try:
            item = Item.objects.get(pk=item_pk)
        except Item.DoesNotExist as e:
            data = {'detail': e.message}
            return Response(data, status=status.HTTP_404_NOT_FOUND)

        term_data = request.data
        try:
            taxonomy = Taxonomy.objects.get(slug=term_data['taxonomy'])
        except Taxonomy.DoesNotExist as e:
            data = {'detail': e.message}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        terms = []
        for term_name in term_data.getlist('name'):
            try:
                term = Term.objects.by_taxonomy(
                    taxonomy=taxonomy,
                    name=term_name,
                )
            except Term.DoesNotExist as e:
                data = {'detail': e.message}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)

            terms.append(term)

        item.apply_terms(terms)

        serializer = ItemSerializer(item)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @detail_route(methods=['post'])
    def delete_all_terms(self, request, item_pk):
        taxonomy_slug = request.data['taxonomy']

        try:
            item = Item.objects.get(pk=item_pk)
        except Item.DoesNotExist as e:
            data = {'detail': e.message}
            return Response(data, status=status.HTTP_404_NOT_FOUND)

        try:
            taxonomy = Taxonomy.objects.get(slug=taxonomy_slug)
        except Taxonomy.DoesNotExist as e:
            message = _("Taxonomy with slug '%s' does not exist.") % (
                taxonomy_slug,
            )

            data = {'detail': message}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        item.delete_all_terms(taxonomy)

        serializer = ItemSerializer(item)

        return Response(serializer.data, status=status.HTTP_200_OK)


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
