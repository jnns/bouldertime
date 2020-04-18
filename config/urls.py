import rest_framework.urls
from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from core.views import GymDetail, GymList

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", GymList.as_view(),),
    path("<slug:gym>", GymDetail.as_view(),),
    path(r"^api-auth/", rest_framework.urls),
]


if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
