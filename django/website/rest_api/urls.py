from django.conf.urls import patterns, include, url

from rest_framework import routers


from .views import (
    ItemViewSet,
    TaxonomyViewSet,
    TermViewSet,
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

urlpatterns = router.urls
