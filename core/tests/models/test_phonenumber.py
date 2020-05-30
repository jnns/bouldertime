import hashlib

import pytest
from django.utils.timezone import now

from core.models import PhoneNumber

pytestmark = pytest.mark.django_db


def test_init():
    assert str(PhoneNumber())
    assert (
        str(PhoneNumber(plain_number="+491234567890"))
        == "9bd6ad2d480f48e483d87fb7bf456c2ad0dc3744"
    )


def test_hashed_number():
    hashed_number = hashlib.sha1(b"+491234567890").hexdigest()
    assert str(PhoneNumber.objects.create("+491234567890")) == hashed_number


def test_verify():
    pre = now()
    phone_number = PhoneNumber(plain_number="01234567890")
    phone_number.verify()
    post = now()
    assert pre < phone_number.verified_at < post
