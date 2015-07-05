from rest_framework import routers

from .views import ItemViewSet

router = routers.SimpleRouter()
router.register(r'items', ItemViewSet)
urlpatterns = router.urls
