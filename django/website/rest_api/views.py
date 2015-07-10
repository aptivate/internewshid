from rest_framework_bulk.mixins import BulkDestroyModelMixin
from rest_framework import viewsets

from data_layer.models import Item
from .serializers import ItemSerializer


class ItemViewSet(viewsets.ModelViewSet, BulkDestroyModelMixin):
    serializer_class = ItemSerializer
    filter_fields = ('created', 'body', 'timestamp', )

    def get_queryset(self):
        items = Item.objects.all()
        ids = self.request.query_params.getlist('ids')
        if ids:
            items = items.filter(id__in=ids)

        return items
