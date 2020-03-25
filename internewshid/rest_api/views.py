from functools import reduce

from django.db.models import Count, Q
from django.utils.translation import ugettext as _

from rest_framework import status, viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_bulk.mixins import BulkDestroyModelMixin
from rest_pandas import PandasView

from data_layer.models import Item
from taxonomies.models import Taxonomy, Term

from .serializers import (
    ItemExportSerializer, ItemSerializer, LocationCoverageSerializer,
    TaxonomySerializer, TermItemCountSerializer, TermSerializer
)


class ItemViewSet(viewsets.ModelViewSet, BulkDestroyModelMixin):
    serializer_class = ItemSerializer
    pagination_class = LimitOffsetPagination
    filter_fields = (
        'created',
        'body',
        'translation',
        'location',
        'sub_location',
        'language',
        'risk',
        'gender',
        'age',
        'contributor',
        'collection_type',
        'timestamp',
    )

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
            if term:
                matches = Term.objects.filter(
                    name=term, taxonomy__slug=taxonomy
                )
                if len(matches) == 0:
                    # If the term doesn't exist, there can be no matches
                    return Item.objects.none()

                items = items.filter(terms__id=matches[0].id)

        # Filter on any of these terms
        terms_or = [t.split(':', 1) for t in self.request.query_params.getlist(
            'terms_or', []
        )]

        if len(terms_or) > 0:
            terms_or_q = reduce(
                lambda x, y: x | y,
                [(Q(taxonomy__slug=tx) & Q(name=tm))
                 for (tx, tm) in terms_or]
            )
            matching_terms = Term.objects.filter(terms_or_q)

            items = items.filter(terms__in=matching_terms)

        location = self.request.query_params.get('location', None)
        if location is not None:
            items = items.filter(location__icontains=location)

        sub_location = self.request.query_params.get('sub_location', None)
        if sub_location is not None:
            items = items.filter(sub_location__icontains=sub_location)

        gender = self.request.query_params.get('gender', None)
        if gender is not None:
            items = items.filter(gender__icontains=gender)

        from_age = self.request.query_params.get('from_age', None)
        to_age = self.request.query_params.get('to_age', None)

        if from_age is not None and to_age is not None:
            items = items.filter(age__range=[from_age, to_age])

        contributor = self.request.query_params.get('contributor', None)
        if contributor is not None:
            items = items.filter(contributor__icontains=contributor)

        collection_type = self.request.query_params.get('collection_type', None)
        if collection_type is not None:
            items = items.filter(collection_type__icontains=collection_type)

        start_time = self.request.query_params.get('start_time', None)
        end_time = self.request.query_params.get('end_time', None)
        if start_time is not None and end_time is not None:
            items = items.filter(timestamp__range=[start_time, end_time])

        external_id_pattern = self.request.query_params.get(
            'external_id_pattern', None)
        if external_id_pattern is not None:
            items = items.filter(external_id__contains=external_id_pattern)

        search = self.request.query_params.get('search', None)
        if search is not None:
            # Either the translation or body must match all the keywords
            # Anything more sophisticated and we should use a search backend
            words = search.split()
            body_q = reduce(
                lambda x, y: x & y, [Q(body__icontains=w) for w in words]
            )
            translation_q = reduce(
                lambda x, y: x & y, [Q(translation__icontains=w)
                                     for w in words]
            )

            items = items.filter(body_q | translation_q)

        ordering = self.request.query_params.get('ordering', '-timestamp')
        items = items.order_by(ordering)

        return items

    @action(methods=['post'], detail=True)
    def add_terms(self, request, item_pk):
        try:
            item = Item.objects.get(pk=item_pk)
        except Item.DoesNotExist as e:
            data = {'detail': str(e)}
            return Response(data, status=status.HTTP_404_NOT_FOUND)

        term_data = request.data
        try:
            taxonomy = Taxonomy.objects.get(slug=term_data['taxonomy'])
        except Taxonomy.DoesNotExist as e:
            data = {'detail': str(e)}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        terms = []
        for term_name in term_data.getlist('name'):
            try:
                term = Term.objects.by_taxonomy(
                    taxonomy=taxonomy,
                    name=term_name,
                )
            except Term.DoesNotExist as e:
                data = {'detail': str(e)}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)

            terms.append(term)

        item.apply_terms(terms)

        serializer = ItemSerializer(item)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True)
    def delete_all_terms(self, request, item_pk):
        taxonomy_slug = request.data['taxonomy']

        try:
            item = Item.objects.get(pk=item_pk)
        except Item.DoesNotExist as e:
            data = {'detail': str(e)}
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

    @action(methods=['get'], detail=True)
    def itemcount(self, request, slug):
        try:
            taxonomy = Taxonomy.objects.get(slug=slug)
        except Taxonomy.DoesNotExist:
            message = _("Taxonomy with slug '{0}' does not exist.").format(slug)

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


class LocationCoverageView(PandasView):
    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Item.objects.all()
    serializer_class = LocationCoverageSerializer

    def get(self, *args, **kwargs):
        response = super(LocationCoverageView, self).get(*args, **kwargs)
        filename = 'attachment;filename={}'.format('location-coverage.csv')
        response['Content-Disposition'] = filename
        return response


class ItemExportView(PandasView):
    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Item.objects.all()
    serializer_class = ItemExportSerializer

    def get(self, *args, **kwargs):
        response = super(ItemExportView, self).get(*args, **kwargs)
        filename = 'attachment;filename={}'.format('item-export.csv')
        response['Content-Disposition'] = filename
        return response
