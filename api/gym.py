from rest_framework import serializers, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import Gym


class GymSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="gym-detail", lookup_field="slug"
    )
    attendance = serializers.JSONField()

    class Meta:
        model = Gym
        fields = ["url", "attendance"]


class GymViewSet(viewsets.ModelViewSet):
    queryset = Gym.objects.all()
    serializer_class = GymSerializer
    lookup_field = "slug"

    @action(detail=True, methods=["get"])
    def bookables(self, request, slug):
        gym = self.get_object()
        return Response(gym.get_bookables())
