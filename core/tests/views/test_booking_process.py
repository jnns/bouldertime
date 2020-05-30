from datetime import time
from unittest.mock import patch

import pytest
from django.urls import reverse
from django.utils.timezone import localdate

from core.models import Gym


@pytest.fixture
def gym():
    return Gym.objects.create(
        name="Example Gym", slug="example-gym", opens_at=time(10), closes_at=time(22)
    )


@pytest.mark.django_db
@patch("core.models.booking.get_identifier")
def test_booking(get_identifier, gym, client):
    get_identifier.return_value = "12-hippopotamus"
    booking_data = {
        "date": localdate(),
        "start": 14,
        "end": 16,
        "phone_no": "+49123456789",
    }
    gym_url = reverse("booking-create", kwargs={"gym": "example-gym"})
    response = client.post(gym_url, booking_data, follow=True)
    assert "12-hippopotamus" in response.content.decode()
    assert "2 p.m." in response.content.decode()
    assert "4 p.m." in response.content.decode()


@pytest.mark.django_db
def test_csrf_token(client, gym_factory):
    gym = gym_factory()
    booking_create_url = reverse("booking-create", kwargs={"gym": gym.slug})
    response = client.get(booking_create_url)
    assert "csrftoken" in response.cookies
