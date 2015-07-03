from django.conf.urls import url
from .views import ItemList, ItemView

urlpatterns = [
    url(r'items/', ItemList.as_view(), name="item_list"),
    url(r'items/(?P<pk>[0-9]+)', ItemView.as_view(), name="item_view"),
]
