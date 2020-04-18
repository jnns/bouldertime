from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path

from core.views import GymDetail, GymList

urlpatterns = [
    re_path(r"^api-auth/", include("rest_framework.urls")),
    path("api/", include("api.urls")),
    path("admin/", admin.site.urls),
    path("<slug:gym>/", GymDetail.as_view(),),
    path("", GymList.as_view(),),
]


if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
