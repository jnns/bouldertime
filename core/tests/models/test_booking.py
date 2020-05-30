import re
from datetime import date, time
from unittest import mock

import pytest
from django.db import transaction
from django.urls import reverse
from django.utils.timezone import now

from core.models import Booking, Gym, PhoneNumber
from core.utils import get_identifier


@pytest.fixture
def gym():
    return Gym.objects.create(
        name="Example Gym", slug="example-gym", opens_at=time(10), closes_at=time(22)
    )


@pytest.mark.django_db
def test_pin(gym):
    booking = Booking.objects.create(
        gym=gym,
        date=date.today(),
        start=time(14),
        end=time(15),
        phone_number="+49123456789",
    )
    assert 1000 <= booking.pin <= 9999


@pytest.mark.parametrize(
    "attempts,num_of_identifiers",
    [(0, 10), (1, 100), (2, 1000), (3, 10000), (4, 30000)],
)
def test_get_identifier(attempts, num_of_identifiers):
    used = [get_identifier(attempts) for _ in range(num_of_identifiers)]
    assert len(set(used)) == len(used)


@pytest.mark.django_db
@mock.patch("core.models.booking.get_identifier")
def test_name_constraint(get_identifier, booking_factory):
    get_identifier.return_value = "always-the-same-name"
    booking_factory()

    with pytest.raises(Booking.MaximumNameCollisionError):
        with transaction.atomic():
            booking_factory()

    booking_factory(status=Booking.STATUS_NOSHOW)
    booking_factory(status=Booking.STATUS_CANCELLED)


@pytest.mark.django_db
@mock.patch("core.models.booking.get_identifier")
def test_name_generation(get_identifier, booking_factory):
    from core.utils import get_identifier as original_get_identifier

    get_identifier.return_value = original_get_identifier()

    existing_name = booking_factory().name

    get_identifier.side_effect = lambda attempts: {
        0: existing_name,
        1: existing_name,
        2: existing_name,
        3: original_get_identifier(2),
    }[attempts]

    second_name = booking_factory().name

    assert re.match(r"\d{1,3}-\w+-\w+-\w+", second_name)


@pytest.mark.django_db
def test_create_booking(gym_factory):
    booking = Booking.objects.create(
        gym=gym_factory(name="example"),
        phone_number="+49123456789",
        start="10:00",
        end="12:00",
    )
    assert booking.phone_number.id

    booking = Booking.objects.create(
        gym=gym_factory(name="example"),
        phone_number=PhoneNumber.objects.create("+49234567890"),
        start="10:00",
        end="12:00",
    )
    assert booking.phone_number.id


@pytest.mark.django_db
def test_create_booking_with_existing_phone_number(gym_factory):
    booking_1 = Booking.objects.create(
        gym=gym_factory(name="example"),
        phone_number="+49123456789",
        start="10:00",
        end="12:00",
    )
    booking_2 = Booking.objects.create(
        gym=gym_factory(name="example"),
        phone_number="+49123456789",
        start="13:00",
        end="16:00",
    )
    assert booking_1.phone_number == booking_2.phone_number


@pytest.mark.django_db
def test_confirm(booking_factory):
    booking = booking_factory()
    pre = now()
    booking.confirm()
    post = now()
    assert pre <= booking.phone_number.verified_at <= post
    assert booking.status == booking.STATUS_CONFIRMED


@pytest.mark.django_db
def test_ical(client, booking_factory):

    booking = booking_factory()
    ical_url = reverse("booking-calendar-file", kwargs={"booking": booking.name})
    response = client.get(ical_url)
    content = response.content.decode()
    assert response["Content-Type"] == "text/calendar"
    assert content.startswith("BEGIN:VCALENDAR")
    assert content.endswith("END:VCALENDAR\n")
    assert str(booking.gym) in content
