import random
from datetime import date

from django.db import models, transaction
from django.db.utils import IntegrityError
from django.urls import reverse
from django.utils.timezone import now

from core.utils import get_identifier

system_random = random.SystemRandom()


def pin():
    return system_random.randint(1111, 9999)


class Booking(models.Model):
    STATUS_NEW = "NEW"
    STATUS_EXPIRED = "EXPIRED"
    STATUS_CONFIRMED = "CONFIRMED"
    STATUS_CANCELED = "CANCELED"
    STATUS_NOSHOW = "NOSHOW"

    name = models.CharField(max_length=255)
    pin = models.PositiveSmallIntegerField(default=pin)
    status = models.CharField(
        max_length=255,
        choices=[
            (STATUS_NEW, STATUS_NEW),
            (STATUS_EXPIRED, STATUS_EXPIRED),
            (STATUS_CONFIRMED, STATUS_CONFIRMED),
            (STATUS_CANCELED, STATUS_CANCELED),
            (STATUS_NOSHOW, STATUS_NOSHOW),
        ],
        default=STATUS_NEW,
    )
    created_at = models.DateTimeField(default=now)
    gym = models.ForeignKey("Gym", on_delete=models.CASCADE)
    phone_no_hash = models.CharField(max_length=255)
    date = models.DateField(default=date.today)
    start = models.TimeField()
    end = models.TimeField()
    checkin_at = models.TimeField(null=True)
    checkout_at = models.TimeField(null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name"],
                condition=models.Q(status__in=["NEW", "CONFIRMED"]),
                name="unique_name",
            )
        ]

    class MaximumNameCollisionError(Exception):
        pass

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("booking-detail", kwargs={"booking": self.name})

    def save(self, *args, **kwargs):
        for attempt in range(0, 100):
            self.name = get_identifier(attempt)
            try:
                with transaction.atomic():
                    return super().save(*args, **kwargs)
            except IntegrityError as e:
                if "unique_name" not in str(e):
                    raise
        raise Booking.MaximumNameCollisionError

    def send_pin(self):
        sms = "Hello. Please confirm your booking by entering this code: 1234"
        print(sms)
