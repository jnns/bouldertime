import pytest
from django.urls import reverse
from django.utils.timezone import now

from core.models import Booking

pytestmark = pytest.mark.django_db


@pytest.mark.xfail
def test_scan_new():
    assert False


@pytest.mark.xfail
def test_authorization():
    assert False


def test_post_anonymous(booking_factory, client):
    booking = booking_factory(status=Booking.STATUS_CONFIRMED)
    response = client.post(booking.get_absolute_url())
    assert response.url.startswith("/admin/")


@pytest.mark.xfail(reason="permission check not yet implemented.")
def test_post_authenticated(booking_factory, client, user_factory):
    user = user_factory()
    booking = booking_factory(status=Booking.STATUS_CONFIRMED)
    client.force_login
    response = client.post(booking.get_absolute_url())
    assert response.url == booking.get_absolute_url()


def test_post_confirmed(booking_factory, admin_client):
    booking = booking_factory(status=Booking.STATUS_CONFIRMED)
    booking_url = reverse("booking-detail", kwargs={"booking": booking.name})
    pre = now().time()
    admin_client.post(booking_url, data={"checkin_at": now().time()})
    booking.refresh_from_db()
    assert pre < booking.checkin_at < now().time()


def test_post_checkedin(booking_factory, admin_client):
    booking = booking_factory(status=Booking.STATUS_CONFIRMED, checkin_at=now().time())
    booking_url = reverse("booking-detail", kwargs={"booking": booking.name})
    pre = now().time()
    admin_client.post(booking_url, data={})
    booking.refresh_from_db()
    assert pre < booking.checkout_at < now().time()
