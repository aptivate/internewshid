from django.conf.urls import patterns, include

from rest_framework import routers


from .views import (
    ItemViewSet,
    TaxonomyViewSet,
    TermCountViewSet,
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
    r'terms/(?P<taxonomy>[\w-]+)/itemcount',
    TermCountViewSet,
    base_name='term',
)
router.register(
    r'terms',
    TermViewSet,
)

urlpatterns = router.urls
