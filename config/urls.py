from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path

from core.views import (
    BookingCalendarFile,
    BookingCancellation,
    BookingCreate,
    BookingDetail,
    BookingVerification,
    Dashboard,
    GymList,
)

urlpatterns = [
    re_path(r"^api-auth/", include("rest_framework.urls")),
    path("api/", include("api.urls")),
    path("admin/", admin.site.urls),
    path("bookings/<slug:booking>/", BookingDetail.as_view(), name="booking-detail"),
    path(
        "bookings/<slug:booking>/verify/",
        BookingVerification.as_view(),
        name="booking-verification",
    ),
    path(
        "bookings/<slug:booking>/cancel/",
        BookingCancellation.as_view(),
        name="booking-cancellation",
    ),
    path(
        "bookings/<slug:booking>.ics",
        BookingCalendarFile.as_view(),
        name="booking-calendar-file",
    ),
    path("<slug:gym>/", BookingCreate.as_view(), name="booking-create"),
    path("<slug:gym>/dashboard/", Dashboard.as_view(template_name="dashboard.html")),
    path("", GymList.as_view(),),
]


if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
