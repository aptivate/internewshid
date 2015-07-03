from rest_framework import generics
from data_layer.models import Item
from .serializers import ItemSerializer


class ItemList(generics.ListCreateAPIView):

    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    filter_fields = ('created', 'body', 'timestamp', )


class ItemView(generics.DestroyAPIView):

    queryset = Item.objects.all()


