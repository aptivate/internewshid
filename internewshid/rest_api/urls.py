from django.conf.urls import url

from rest_framework import routers

from .views import (
    ItemExportView, ItemViewSet, LocationCoverageView, TaxonomyViewSet,
    TermViewSet
)

router = routers.SimpleRouter()
router.register(
    r'items',
    ItemViewSet,
    base_name='item'  # TODO: remove when Message model renamed Item
)
router.register(
    r'taxonomies',
    TaxonomyViewSet,
)
router.register(
    r'terms',
    TermViewSet,
)

urlpatterns = [
    url(
        r'location-coverage/$',
        LocationCoverageView.as_view(),
        name='location-coverage'
    ),
    url(
        r'item-export/$',
        ItemExportView.as_view(),
        name='item-export'
    ),
] + router.urls
