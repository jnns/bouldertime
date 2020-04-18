from datetime import time
from unittest.mock import patch

import pytest

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


@patch("core.models.Gym.get_attendance")
def test_get_bookables(mocked_get_attendance):
    mocked_get_attendance.return_value = {
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
    bookables = Gym(opens_at=time(8), closes_at=time(17)).get_bookables()
    assert bookables == {
        8: [],
        9: [10, 11, 12],
        10: [11, 12],
        11: [12],
        12: [],
        13: [14, 15],
        14: [15],
        15: [],
        16: [17],
    }
