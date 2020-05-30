from hashlib import sha1

from django.db import models
from django.utils.timezone import now


class PhoneNumberManager(models.Manager):
    def create(self, plain_number, *args, **kwargs):
        kwargs["hashed_number"] = PhoneNumber(plain_number=plain_number).hashed_number
        return super().create(*args, **kwargs)

    def get_or_create(self, defaults=None, **kwargs):
        if "plain_number" in kwargs:
            kwargs["hashed_number"] = PhoneNumber(
                plain_number=kwargs.pop("plain_number")
            ).hashed_number
        return super().get_or_create(defaults, **kwargs)

    def blocked(self):
        return self.get_queryset().filter(blocked_due_to__isnull=False)


class PhoneNumber(models.Model):
    hashed_number = models.CharField(unique=True, default=None, max_length=255)
    verified_at = models.DateTimeField(null=True)
    blocked_due_to = models.ForeignKey("Booking", on_delete=models.CASCADE, null=True)

    objects = PhoneNumberManager()

    def __str__(self):
        return self.hashed_number or "None"

    def __init__(self, *args, **kwargs):
        plain_number = kwargs.pop("plain_number", None)
        super().__init__(*args, **kwargs)
        if plain_number:
            self.hashed_number = sha1(plain_number.encode("utf-8")).hexdigest()

    def verify(self):
        assert self.hashed_number
        self.verified_at = now()
        if self.id:
            self.save(update_fields=["verified_at"])
        else:
            self.save()

    @property
    def is_blocked(self):
        return bool(self.blocked_due_to)

    def block(self, booking):
        self.blocked_due_to = booking
        self.save(update_fields=["blocked_due_to"])
