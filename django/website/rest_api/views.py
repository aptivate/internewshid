from rest_framework import generics
from rest_framework_bulk.mixins import BulkDestroyModelMixin
from rest_framework import viewsets

from data_layer.models import Item
from .serializers import ItemSerializer


class ItemViewSet(viewsets.ModelViewSet, BulkDestroyModelMixin):
    serializer_class = ItemSerializer
    queryset = Item.objects.all()
    filter_fields = ('created', 'body', 'timestamp', )
