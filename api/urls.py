from django.conf.urls import include, url
from rest_framework import routers

from .gym import GymViewSet

router = routers.DefaultRouter()
router.register(r"gyms", GymViewSet)

urlpatterns = [
    url(r"^", include(router.urls)),
]
