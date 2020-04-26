from django import forms

from core.models import Booking, Gym


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
    phone_no = forms.CharField()

    class Meta:
        model = Booking
        fields = ["start", "end", "phone_no", "gym"]
