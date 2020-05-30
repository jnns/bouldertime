import json
from datetime import datetime

from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import CreateView, DetailView, FormView, UpdateView
from django.views.generic.detail import SingleObjectMixin

from .forms import BookingForm, GymForm, VerificationForm
from .models import Booking, Gym


class GymList(FormView):
    template_name = "core/gym_list.html"
    form_class = GymForm

    def get_context_data(self, **kwargs):
        gyms = json.dumps(list(Gym.objects.values("id", "slug", "name")))
        return super().get_context_data(gyms=gyms, **kwargs)


class BookingCancellation(UpdateView):
    model = Booking
    slug_url_kwarg = "booking"
    slug_field = "name"
    fields = []
    template_name_suffix = "_cancel_form"

    def form_valid(self, form):
        self.object.status = Booking.STATUS_CANCELLED
        return super().form_valid(form)


class BookingCreate(CreateView):
    template_name = "core/booking_create_form.html"
    form_class = BookingForm

    @method_decorator(ensure_csrf_cookie)
    def dispatch(self, *args, **kwargs):
        self.gym = Gym.objects.get(slug=self.kwargs.get("gym"))
        return super().dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if "data" in kwargs:
            kwargs["data"] = kwargs["data"].dict()
            kwargs["data"]["gym"] = self.gym
        return kwargs

    def get_context_data(self, **kwargs):
        context = {
            "gym": self.gym,
            "attendance": json.dumps(self.gym.attendance),
            "bookables": json.dumps(self.gym.get_bookables()),
        }
        return super().get_context_data(**context, **kwargs)

    def get_success_url(self):
        if self.object.status == Booking.STATUS_CONFIRMED:
            return reverse("booking-detail", kwargs={"booking": self.object.name})
        return reverse("booking-verification", kwargs={"booking": self.object.name})


class BookingDetail(UserPassesTestMixin, UpdateView):
    model = Booking
    slug_url_kwarg = "booking"
    slug_field = "name"
    template_context_name = "booking"
    template_name_suffix = "_detail"
    fields = []
    login_url = "/admin/"

    def test_func(self):
        method_is_POST = self.request.method == "POST"
        user_not_authenticated = not self.request.user.is_authenticated
        return not (method_is_POST and user_not_authenticated)

    def get_context_data(self, **kwargs):
        if self.request.user.is_authenticated:
            if self.object.get_status_display() != "CHECKED IN":
                form_caption = "check in"
            else:
                form_caption = "check out"
            context = {"form_caption": form_caption}
        else:
            context = {"qr_code": self.object.qr_code(self.request)}
        return super().get_context_data(**{**kwargs, **context})

    def form_valid(self, form):
        if self.object.get_status_display() == "CHECKED IN":
            self.object.check_out()
        else:
            self.object.check_in()
        return HttpResponseRedirect(self.get_success_url())


class BookingScan(DetailView):
    model = Booking
    slug_url_kwarg = "booking"
    slug_field = "name"

    def get(self, *args, **kwargs):
        self.object = self.get_object()
        self.object.checkin_at = now()
        self.object.save(update_fields=["checkin_at", "checkout_at"])
        return super().get(*args, **kwargs)


class BookingCalendarFile(BookingDetail):
    content_type = "text/calendar"
    template_name = "core/calendar.ics"

    def get_context_data(self, **kwargs):
        ical_date_format = "%Y%m%dT%H%M%S"
        start = datetime.combine(self.object.date, self.object.start).strftime(
            ical_date_format
        )
        end = datetime.combine(self.object.date, self.object.end).strftime(
            ical_date_format
        )
        cancellation_url = self.request.build_absolute_uri(
            reverse("booking-cancellation", kwargs={"booking": self.object.name})
        )
        url = self.request.build_absolute_uri(self.object.get_absolute_url())
        return super().get_context_data(
            start=start, end=end, url=url, cancellation_url=cancellation_url,
        )


class BookingVerification(SingleObjectMixin, FormView):
    form_class = VerificationForm
    template_name = "core/booking_verification.html"
    model = Booking
    slug_url_kwarg = "booking"
    slug_field = "name"
    template_context_name = "booking"

    def get_initial(self):
        return {"booking": self.object.name}

    def dispatch(self, *args, **kwargs):
        self.object = self.get_object()
        if self.object.status != Booking.STATUS_NEW:
            return redirect(self.object)
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        self.object.confirm()
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.get_absolute_url()


class Dashboard(DetailView):
    model = Gym
    template_name = "dashboard.html"
    slug_url_kwarg = "gym"
    slug_field = "slug"
