from django import forms

from .models import Gym


class GymForm(forms.Form):
    gym = forms.ModelChoiceField(queryset=Gym.objects.all(), to_field_name="slug",)
