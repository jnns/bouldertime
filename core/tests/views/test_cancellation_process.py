import pytest
from django.urls import reverse

from core.models import Booking

pytestmark = pytest.mark.django_db


def test_cancellation_link(client, booking_factory):
    booking = booking_factory(status=Booking.STATUS_CONFIRMED)
    response = client.get(booking.get_absolute_url())
    cancellation_url = reverse("booking-cancellation", kwargs={"booking": booking.name})
    assert cancellation_url in response.content.decode()
    assert "Cancel this booking" in response.content.decode()


def test_cancellation_confirmation(client, booking_factory):
    booking = booking_factory(status=Booking.STATUS_CONFIRMED)
    cancellation_url = reverse("booking-cancellation", kwargs={"booking": booking.name})
    response = client.get(cancellation_url)
    assert "Are you sure" in response.content.decode()
    response = client.post(cancellation_url)
    assert response.url == booking.get_absolute_url()
    response = client.get(response.url)
    assert "CANCELLED" in response.content.decode()
