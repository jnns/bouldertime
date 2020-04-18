from rest_framework import serializers, viewsets

from core.models import Gym


class GymSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="gym-detail", lookup_field="slug"
    )
    attendance = serializers.JSONField(source="get_attendance")

    class Meta:
        model = Gym
        fields = ["url", "attendance"]


class GymViewSet(viewsets.ModelViewSet):
    queryset = Gym.objects.all()
    serializer_class = GymSerializer
    lookup_field = "slug"
