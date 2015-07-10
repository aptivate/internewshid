from rest_framework import routers
from rest_framework_bulk.routes import BulkRouter

from .views import ItemViewSet

router = BulkRouter()
router.register(
    r'items',
    ItemViewSet,
    base_name='item'  # TODO: remove when Message model renamed Item
)
urlpatterns = router.urls
