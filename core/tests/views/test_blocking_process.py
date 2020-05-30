import pytest
from django.utils.timezone import localdate

from core.tests.conftest import create_booking

pytestmark = pytest.mark.django_db


def test_booking_with_blocked_number(client, booking_factory):
    phone_number = "+491234567890"
    booking_1 = booking_factory(phone_number=phone_number)
    booking_1.block_phone_number()
    response = create_booking(
        client,
        booking_1.gym,
        date=localdate(),
        start="10:00",
        end="11:00",
        phone_number=phone_number,
    )
    content = response.content.decode()
    assert "blocked" in content
    assert str(booking_1.start) in content
    assert str(booking_1.gym) in content
    assert str(booking_1.date) in content
