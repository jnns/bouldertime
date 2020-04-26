import json

from django.views.generic import CreateView, DetailView, FormView

from .forms import BookingForm, GymForm
from .models import Booking, Gym


class GymList(FormView):
    template_name = "core/gym_list.html"
    form_class = GymForm


class BookingCreate(CreateView):
    template_name = "core/booking_create_form.html"
    form_class = BookingForm

    def dispatch(self, *args, **kwargs):
        self.gym = Gym.objects.get(slug=self.kwargs.get("gym"))
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = {
            "gym": self.gym,
            "attendance": json.dumps(self.gym.get_attendance()),
            "bookables": json.dumps(self.gym.get_bookables()),
        }
        return super().get_context_data(**context, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if "data" in kwargs:
            kwargs["data"] = kwargs["data"].dict()
            kwargs["data"]["gym"] = self.gym
        return kwargs

    def get_success_url(self):
        return self.object.get_absolute_url()


class BookingDetail(DetailView):
    model = Booking
    slug_url_kwarg = "booking"
    slug_field = "name"
