import pytest

from core.models import Booking
from core.tests.conftest import try_to_verify

pytestmark = pytest.mark.django_db


def test_booking_confirmation_failed(client, booking_factory):
    booking = booking_factory(start="10:00", end="12:00", pin=1234)
    assert (
        "Confirmation code is not correct"
        in try_to_verify(client, booking, 9999).content.decode()
    )


def test_booking_confirmation_success(client, booking_factory):
    booking = booking_factory(start="10:00", end="12:00", pin=1234)
    assert try_to_verify(client, booking, 1234).url == booking.get_absolute_url()


def test_booking_confirmation_status_change(client, booking_factory):
    booking = booking_factory(start="10:00", end="12:00", pin=1234)
    response = client.get(try_to_verify(client, booking, 1234).url).content.decode()
    assert "Status: CONFIRMED" in response


def test_confirmed_booking_redirects_to_detail_page(client, booking_factory):
    booking = booking_factory(status=Booking.STATUS_CONFIRMED)
    assert try_to_verify(client, booking, booking.pin).url == booking.get_absolute_url()
