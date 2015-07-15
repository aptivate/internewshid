from rest_framework_bulk.routes import BulkRouter

from .views import (
    ItemViewSet,
    TaxonomyViewSet,
    TermViewSet,
)

router = BulkRouter()
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
