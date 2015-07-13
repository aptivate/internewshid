from rest_framework_bulk.mixins import BulkDestroyModelMixin
from rest_framework import viewsets

from data_layer.models import (
    Item,
    Taxonomy,
)
from .serializers import (
    ItemSerializer,
    TaxonomySerializer,
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


class TaxonomyViewSet(viewsets.ModelViewSet):
    serializer_class = TaxonomySerializer

    queryset = Taxonomy.objects.all()
