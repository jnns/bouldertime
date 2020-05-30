from datetime import time, timedelta
from unittest.mock import PropertyMock, patch

import pytest
from django.utils.timezone import localdate

from core.models import Gym


@pytest.mark.parametrize(
    "opens_at,closes_at,expected",
    [
        (time(8), time(22), range(8, 22)),
        (time(10), time(22), range(10, 22)),
        (time(10), time(23), range(10, 23)),
    ],
)
def test_get_opening_hours(opens_at, closes_at, expected):
    gym = Gym(opens_at=opens_at, closes_at=closes_at)
    assert list(gym.get_opening_hours()) == list(expected)


@patch("core.models.Gym.attendance", new_callable=PropertyMock)
def test_get_bookables(mocked_attendance):
    mocked_attendance.return_value = {
        str(localdate()): {
            8: 100,
            9: 0,
            10: 0,
            11: 0,
            12: 100,
            13: 0,
            14: 0,
            15: 100,
            16: 0,
        }
    }
    gym = Gym(opens_at=time(8), closes_at=time(17))
    assert gym.get_bookables() == {
        str(localdate()): {
            8: [],
            9: [10, 11, 12],
            10: [11, 12],
            11: [12],
            12: [],
            13: [14, 15],
            14: [15],
            15: [],
            16: [17],
        },
        str(localdate() + timedelta(days=1)): {
            8: [],
            9: [],
            10: [],
            11: [],
            12: [],
            13: [],
            14: [],
            15: [],
            16: [],
        },
        str(localdate() + timedelta(days=2)): {
            8: [],
            9: [],
            10: [],
            11: [],
            12: [],
            13: [],
            14: [],
            15: [],
            16: [],
        },
    }


@pytest.mark.django_db
def test_attendance(booking_factory):
    booking = booking_factory(
        start="10:00",
        end="11:00",
        phone_number="+49123456789",
        gym__max_guests=4,
        gym__opens_at=time(10),
        gym__closes_at=time(12),
    )
    booking_factory(
        start="10:00",
        end="11:00",
        phone_number="+49123456789",
        gym=booking.gym,
        status=booking.STATUS_CANCELLED,
    )
    today = localdate()
    assert booking.gym.attendance == {
        str(today): {10: 25, 11: 0},
        str(today + timedelta(days=1)): {10: 0, 11: 0},
        str(today + timedelta(days=2)): {10: 0, 11: 0},
    }


@pytest.mark.django_db
def test_attendance_without_bookings():
    gym = Gym.objects.create(opens_at=time(10), closes_at=time(12), max_guests=4)
    today = localdate()
    assert gym.attendance == {
        str(today): {10: 0, 11: 0},
        str(today + timedelta(days=1)): {10: 0, 11: 0},
        str(today + timedelta(days=2)): {10: 0, 11: 0},
    }
