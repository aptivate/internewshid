from django.conf.urls import url
from .views import ItemList

urlpatterns = [
    url(r'items/', ItemList.as_view(), name="items"),
]
