from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import gettext as _

from core.models import Booking, Gym, PhoneNumber


class PhoneNumberField(forms.CharField):
    default_validators = [RegexValidator(r"^\+[1-9]\d{7,14}$")]

    def to_python(self, value):
        return super().to_python(value).replace(" ", "").replace("/", "")


class IntTimeField(forms.TimeField):
    def to_python(self, value):
        if ":" not in value:
            value = f"{value}:00"
        return super().to_python(value)


class GymForm(forms.Form):
    gym = forms.ModelChoiceField(queryset=Gym.objects.all(), to_field_name="slug",)


class BookingForm(GymForm, forms.ModelForm):
    start = IntTimeField()
    end = IntTimeField()
    phone_no = PhoneNumberField()

    class Meta:
        model = Booking
        fields = ["date", "start", "end", "phone_no", "gym"]

    def clean_phone_no(self):
        plain_phone_number = self.cleaned_data["phone_no"]
        phone_number, _ = PhoneNumber.objects.get_or_create(
            plain_number=plain_phone_number
        )
        if phone_number.is_blocked:
            raise ValidationError(
                "This phone number has been blocked because a previously booked reservation hasn't been used nor canceled."
                "Please make sure that bookings are canceled when you cannot attend to allow others to use that spot."
                "Send us your blocked phone number to hello@bouldertime.eu to have the restriction removed."
                "Unnattended previous booking: %(booking)s",
                code="blocked",
                params={"booking": phone_number.blocked_due_to},
            )
        return plain_phone_number

    def save(self, *args, **kwargs):
        booking = super().save(commit=False)
        booking.save(plain_phone_number=self.cleaned_data["phone_no"])
        return booking


class VerificationForm(forms.Form):
    pin = forms.IntegerField()
    booking = forms.ModelChoiceField(
        queryset=Booking.objects.unconfirmed(),
        to_field_name="name",
        widget=forms.HiddenInput(),
    )

    def clean(self):
        if (
            not Booking.objects.unconfirmed()
            .filter(pin=self.cleaned_data["pin"])
            .exists()
        ):

            raise ValidationError(
                _("Confirmation code is not correct."), code="invalid"
            )
