from rest_framework import views, response
from data_layer import handlers


class ItemList(views.APIView):

    def get(self, request, format=None):
        items = handlers.Item.list()
        return response.Response(items)
