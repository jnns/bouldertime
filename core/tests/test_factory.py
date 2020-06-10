from conftest import Factory, UseFactory

import pytest


@pytest.mark.django_db
def test_factory(booking_factory):
    booking = booking_factory(gym__name="foo")
    assert booking.gym.name == "foo"
