import re
from hashlib import sha1

from django.db import models
from django.utils.timezone import now


class PhoneNumberManager(models.Manager):
    def create(self, phone_number):
        assert phone_number
        phone_number = PhoneNumber.from_number(phone_number)
        return super().create(hash=sha1(phone_number.encode("utf-8")).hexdigest())


class PhoneNumber(models.Model):
    hash = models.CharField(unique=True, max_length=255)
    verified_at = models.DateTimeField(null=True)
    blocked_due_to = models.ForeignKey("Booking", on_delete=models.CASCADE, null=True)

    objects = PhoneNumberManager()

    @staticmethod
    def from_number(value):
        value = value.replace("/", "").replace(" ", "")
        value = re.sub(r"^0049", "+49", value)
        value = re.sub(r"^0", "+49", value)
        return value

    def __str__(self):
        return self.hash

    def verify(self):
        self.verified_at = now()
        if self.id:
            self.save(update_fields=["verified_at"])
        else:
            self.save()
