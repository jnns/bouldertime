import hashlib

import pytest
from django.utils.timezone import now

from core.models import PhoneNumber

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    "real_number", ["01234567890", "0123/4567890", "0123 4567890", "0123 / 4567890"],
)
def test_create_from_real_number(real_number):
    hashed_number = hashlib.sha1(b"+491234567890").hexdigest()
    assert str(PhoneNumber.objects.create(real_number)) == hashed_number


@pytest.mark.parametrize(
    "input,expected",
    [
        ("01234567890", "+491234567890"),
        ("0123 4567890", "+491234567890"),
        ("0123/4567890", "+491234567890"),
        ("0123 / 4567890", "+491234567890"),
        ("00491234567890", "+491234567890"),
        ("0049 123 4567890", "+491234567890"),
        ("0049123/4567890", "+491234567890"),
        ("0049 123 / 4567890", "+491234567890"),
        ("+491234567890", "+491234567890"),
        ("+49 1234567890", "+491234567890"),
        ("+49123 4567890", "+491234567890"),
        ("+49 123/4567890", "+491234567890"),
        ("+49123 / 4567890", "+491234567890"),
        ("+49123 / 4567890", "+491234567890"),
        ("+49123 / 0049 0049", "+4912300490049"),
    ],
)
def test_from_number(input, expected):
    assert PhoneNumber.from_number(input) == expected


def test_verify():
    pre = now()
    phone_no = PhoneNumber()
    phone_no.verify()
    post = now()
    assert pre < phone_no.verified_at < post
