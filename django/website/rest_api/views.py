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

        item.terms.add(term)
        data = {}  # TODO should be the item containing the new term
        return Response(data, status=status.HTTP_200_OK)


class TaxonomyViewSet(viewsets.ModelViewSet):
    serializer_class = TaxonomySerializer

    queryset = Taxonomy.objects.all()


class TermViewSet(viewsets.ModelViewSet):
    serializer_class = TermSerializer

    queryset = Term.objects.all()  # Will need to filter by taxonomy eventually
