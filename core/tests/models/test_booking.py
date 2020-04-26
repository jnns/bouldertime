import re
from datetime import date, time
from unittest import mock

import pytest
from django.db import transaction

from core.models import Booking, Gym
from core.utils import get_identifier


@pytest.fixture
def gym():
    return Gym.objects.create(
        name="Example Gym", slug="example-gym", opens_at=time(10), closes_at=time(22)
    )


@pytest.mark.django_db
def test_pin(gym):
    booking = Booking.objects.create(
        gym=gym, date=date.today(), start=time(14), end=time(15)
    )
    assert 1000 <= booking.pin <= 9999


@pytest.mark.parametrize(
    "attempts,num_of_identifiers", [(0, 100), (1, 1000), (2, 10000), (3, 30000)]
)
def test_get_identifier(attempts, num_of_identifiers):
    used = [get_identifier(attempts) for _ in range(num_of_identifiers)]
    assert len(set(used)) == len(used)


@pytest.mark.django_db
@mock.patch("core.models.booking.get_identifier")
def test_name_constraint(get_identifier, gym):
    get_identifier.return_value = "always-the-same-name"
    defaults = {
        "gym": gym,
        "date": date.today(),
        "start": time(8),
        "end": time(20),
    }
    Booking.objects.create(**defaults)

    with pytest.raises(Booking.MaximumNameCollisionError):
        with transaction.atomic():
            Booking.objects.create(**defaults)

    Booking.objects.create(**defaults, status=Booking.STATUS_NOSHOW)
    Booking.objects.create(**defaults, status=Booking.STATUS_CANCELED)


@pytest.mark.django_db
@mock.patch("core.models.booking.get_identifier")
def test_name_generation(get_identifier, gym):
    from core.utils import get_identifier as original_get_identifier

    get_identifier.return_value = original_get_identifier()

    existing_name = Booking.objects.create(
        gym=gym, date=date.today(), start=time(14), end=time(15)
    ).name

    get_identifier.side_effect = lambda attempts: {
        0: existing_name,
        1: existing_name,
        2: existing_name,
        3: original_get_identifier(2),
    }[attempts]

    second_name = Booking.objects.create(
        gym=gym, date=date.today(), start=time(14), end=time(15)
    ).name

    assert re.match(r"\d{1,3}-\w+-\w+-\w+", second_name)
