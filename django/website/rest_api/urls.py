from rest_framework import routers

from .views import ItemViewSet

router = routers.SimpleRouter()
router.register(
    r'items',
    ItemViewSet,
    base_name='item'  # TODO: remove when Message model renamed Item
)
urlpatterns = router.urls
