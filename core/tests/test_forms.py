from datetime import time

import pytest
from django.core.exceptions import ValidationError

from core.forms import BookingForm, PhoneNumberField
from core.models import Booking, Gym


@pytest.mark.parametrize("input", ["hello world", "01234567890", "00491234567890"])
def test_phonenumberfield_validation_error(input):
    with pytest.raises(ValidationError):
        PhoneNumberField().clean(input)


@pytest.mark.parametrize("input", ["+491234567890", "+49 123 / 4567890"])
def test_phonenumberfield(input):
    assert PhoneNumberField().clean(input) == "+491234567890"


@pytest.mark.django_db
def test_bookingform():
    gym = Gym.objects.create(opens_at=time(8), closes_at=time(22))
    form = BookingForm(
        {
            "date": "2020-05-18",
            "start": "08:00",
            "end": "10:00",
            "phone_no": "+491234567890",
            "gym": gym,
        }
    )
    form.is_valid()
    assert form.save().phone_number.hashed_number


@pytest.mark.django_db
def test_bookingform_with_same_phone_number():
    gym = Gym.objects.create(opens_at=time(8), closes_at=time(22))
    BookingForm(
        {
            "date": "2020-05-18",
            "start": "08:00",
            "end": "10:00",
            "phone_no": "+491234567890",
            "gym": gym,
        }
    ).save()
    BookingForm(
        {
            "date": "2020-05-18",
            "start": "09:00",
            "end": "11:00",
            "phone_no": "+491234567890",
            "gym": gym,
        }
    ).save()
    assert Booking.objects.count() == 2
