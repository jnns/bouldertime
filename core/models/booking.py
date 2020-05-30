import random
from datetime import date
from io import BytesIO

import qrcode
import qrcode.image.svg
from django.db import models, transaction
from django.db.utils import IntegrityError
from django.urls import reverse
from django.utils.timezone import localdate, now

from core.models import PhoneNumber
from core.sms import SMS
from core.utils import get_identifier

system_random = random.SystemRandom()


def pin():
    return system_random.randint(1111, 9999)


class BookingQuerySet(models.QuerySet):
    def unconfirmed(self):
        return self.filter(status=Booking.STATUS_NEW)

    def not_new(self):
        return self.exclude(status=Booking.STATUS_NEW)

    def for_today(self):
        return self.filter(date=localdate())


class BookingManager(models.Manager):
    def create(self, *args, **kwargs):
        if "phone_number" in kwargs and isinstance(kwargs["phone_number"], str):
            kwargs["phone_number"], _ = PhoneNumber.objects.get_or_create(
                plain_number=kwargs["phone_number"]
            )
        return super().create(*args, **kwargs)


class Booking(models.Model):
    STATUS_NEW = "NEW"
    STATUS_EXPIRED = "EXPIRED"
    STATUS_CONFIRMED = "CONFIRMED"
    STATUS_CANCELLED = "CANCELLED"
    STATUS_NOSHOW = "NOSHOW"

    name = models.CharField(max_length=255)
    pin = models.PositiveSmallIntegerField(default=pin)
    status = models.CharField(
        max_length=255,
        choices=[
            (STATUS_NEW, STATUS_NEW),
            (STATUS_EXPIRED, STATUS_EXPIRED),
            (STATUS_CONFIRMED, STATUS_CONFIRMED),
            (STATUS_CANCELLED, STATUS_CANCELLED),
            (STATUS_NOSHOW, STATUS_NOSHOW),
        ],
        default=STATUS_NEW,
    )
    created_at = models.DateTimeField(default=now)
    gym = models.ForeignKey("Gym", on_delete=models.CASCADE)
    phone_number = models.ForeignKey("PhoneNumber", on_delete=models.CASCADE)
    date = models.DateField(default=date.today)
    start = models.TimeField()
    end = models.TimeField()
    checkin_at = models.TimeField(null=True, blank=True)
    checkout_at = models.TimeField(null=True, blank=True)

    objects = BookingManager.from_queryset(BookingQuerySet)()

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
        try:
            start = self.start
            end = self.end
            start = start.strftime("%H:%M")
            end = end.strftime("%H:%M")
        except AttributeError:
            pass
        return f"{self.name}: {self.gym}, {self.date} {start}-{end}"

    def get_absolute_url(self):
        return reverse("booking-detail", kwargs={"booking": self.name})

    def save(self, *args, **kwargs):
        plain_phone_number = kwargs.pop("plain_phone_number", None)
        if plain_phone_number:
            self.phone_number, _ = PhoneNumber.objects.get_or_create(
                plain_number=plain_phone_number
            )

        if self.id:
            return super().save(*args, **kwargs)

        self._save_with_unique_random_identifier(*args, **kwargs)
        self.send_pin(plain_phone_number)

    def _save_with_unique_random_identifier(self, *args, **kwargs):
        for attempt in range(0, 100):
            self.name = get_identifier(attempt)
            try:
                with transaction.atomic():
                    return super().save(*args, **kwargs)
            except IntegrityError as e:
                if "unique_name" not in str(e):
                    raise
        raise Booking.MaximumNameCollisionError

    def get_or_create_phone_number(self):
        if self.phone_number_id:
            return
        try:
            if isinstance(self.phone_number, str):
                self.phone_number = PhoneNumber.objects.get_or_create(
                    defaults={"hashed_number": self.phone_number}
                )
        except PhoneNumber.DoesNotExist:
            return

    def send_pin(self, plain_phone_number):
        message = f"Please confirm your booking at {self.gym} on {self.date} {self.start}-{self.end} with this activation code:\n\n{self.pin}"
        sms = SMS(plain_phone_number, message)
        sms.send()

    def confirm(self):
        self.phone_number.verified_at = now()
        self.phone_number.save(update_fields=["verified_at"])

        self.status = self.STATUS_CONFIRMED
        self.save(update_fields=["status"])

    def check_in(self):
        if self.date == now().date():
            self.checkin_at = now()
            self.checkout_at = None
            self.save(update_fields=["checkin_at", "checkout_at"])

    def check_out(self):
        if self.date == now().date():
            self.checkout_at = now()
            self.save(update_fields=["checkout_at"])

    def block_phone_number(self):
        self.phone_number.block(self)

    def qr_code(self, request):
        img = qrcode.make(
            request.build_absolute_uri(self.get_absolute_url()),
            image_factory=qrcode.image.svg.SvgImage,
            version=1,
            box_size=15,
            border=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
        )
        with BytesIO() as output:
            img.save(output)
            output.seek(0)
            return output.read().decode()

    def get_status_display(self):
        if self.status == self.STATUS_CONFIRMED:
            if self.checkin_at and not self.checkout_at:
                return "CHECKED IN"
            elif self.checkout_at:
                return "CHECKED OUT"
        return self.status
