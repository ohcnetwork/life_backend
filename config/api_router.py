from django.conf import settings
from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter, SimpleRouter
from rest_framework_nested.routers import NestedSimpleRouter


from life.users.api.viewsets.lsg import DistrictViewSet, LocalBodyViewSet, StateViewSet, WardViewSet
from life.users.api.viewsets.users import UserViewSet

from life.app.api.viewsets.lifedata import LifeDataViewSet

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("life/data", LifeDataViewSet)

router.register("users", UserViewSet)

# Local Body / LSG Viewsets
router.register("state", StateViewSet)
router.register("district", DistrictViewSet)
router.register("local_body", LocalBodyViewSet)
router.register("ward", WardViewSet)


app_name = "api"
urlpatterns = [
    url(r"^", include(router.urls)),
]
