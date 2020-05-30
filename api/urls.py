from django.conf.urls import include, url
from rest_framework import routers

from .booking import BookingViewSet
from .gym import GymViewSet

router = routers.DefaultRouter()
router.register(r"gyms", GymViewSet)
router.register(r"bookings", BookingViewSet)

urlpatterns = [
    url(r"^", include(router.urls)),
]
