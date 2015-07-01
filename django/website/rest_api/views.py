from rest_framework import generics
from data_layer.models import Item
from data_layer.serializers import ItemSerializer


class ItemList(generics.ListAPIView):

    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    filter_fields = ('created', 'body', 'timestamp', )
