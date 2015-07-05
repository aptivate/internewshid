from rest_framework import generics
from rest_framework_bulk.mixins import BulkDestroyModelMixin
from rest_framework import viewsets

from data_layer.models import Item
from .serializers import ItemSerializer


class ItemList(generics.ListCreateAPIView, BulkDestroyModelMixin):
    pass
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    filter_fields = ('created', 'body', 'timestamp', )


class ItemView(generics.DestroyAPIView):

    queryset = Item.objects.all()


class ItemViewSet(viewsets.ModelViewSet):
    serializer_class = ItemSerializer
    queryset = Item.objects.all()
    filter_fields = ('created', 'body', 'timestamp', )
