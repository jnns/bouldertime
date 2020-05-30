from rest_framework import mixins, serializers, viewsets

from core.models import Booking


class BookingSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Booking
        fields = [
            "id",
            "name",
            "status",
            "date",
            "start",
            "end",
            "checkin_at",
            "checkout_at",
        ]


class BookingViewSet(
    mixins.ListModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet
):
    queryset = Booking.objects.not_new().for_today().order_by("start", "name")
    serializer_class = BookingSerializer

    def update(self, *args, **kwargs):
        return super().update(*args, **kwargs)
