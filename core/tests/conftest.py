from collections import defaultdict
from datetime import time

import pytest
from django.urls import reverse
from django.utils.timezone import localdate

from core.models import Booking, Gym, User


class UseFactory:
    """Marker class for invoking a factory function."""

    def __init__(self, factory_func):
        self.factory_func = factory_func

    def __repr__(self):
        func = self.factory_func and f'"{self.factory_func}"' or ""
        return f"UseFactory({func})"


class Factory:
    def __init__(self, model, defaults=None, related_factories=None):
        assert model
        self.model = model
        self.defaults = defaults or {}

    def __repr__(self):
        return f"Factory({self.model.__name__}, {self.defaults})"

    def __call__(self, request):
        self.request = request
        self.use_db = "django_db_setup" in request.fixturenames
        return self.create

    def create(self, **kwargs):
        properties = self.defaults.copy()
        properties.update(self.run_factories_for_dunders(kwargs))
        properties = self.run_factories(properties)

        if self.use_db:
            return self.model._default_manager.create(**properties)
        return self.model(**properties)

    def run_factories_for_dunders(self, kwargs):
        related_obj_kwargs = self.pop_dunder_keys(kwargs)

        for model, model_kwargs in related_obj_kwargs.items():
            related_obj_kwargs[model] = self.get_factory(model)(**model_kwargs)

        kwargs.update(related_obj_kwargs)
        return kwargs

    def pop_dunder_keys(self, kwargs):
        related_obj_kwargs = defaultdict(dict)
        for dunder_key in [key for key in kwargs if "__" in key]:
            model, model_attr = dunder_key.split("__")
            if self.get_factory(model) and model_attr:
                model_value = kwargs.pop(dunder_key)
                related_obj_kwargs[model][model_attr] = model_value
        return related_obj_kwargs

    def get_factory(self, modelname):
        use_factory = self.defaults.get(modelname)
        if isinstance(use_factory, UseFactory):
            return self.request.getfixturevalue(
                use_factory.factory_func or f"{modelname}_factory"
            )

    def run_factories(self, defaults):
        for key in defaults:
            factory = self.get_factory(key)
            if factory:
                defaults[key] = factory()
        return defaults


@pytest.fixture
def gym_factory(request):
    return Factory(
        Gym,
        defaults={
            "name": "example gym",
            "slug": "example-gym",
            "opens_at": time(10),
            "closes_at": time(22),
        },
    )(request)


@pytest.fixture
def user_factory(request):
    return Factory(User, defaults={"email": "test@example.com"})(request)


@pytest.fixture
def booking_factory(request):
    return Factory(
        Booking,
        defaults={
            "date": localdate(),
            "gym": UseFactory("gym_factory"),
            "start": "10:00",
            "end": "11:00",
            "phone_number": "+491234567890",
        },
    )(request)


@pytest.fixture
def booking_factory_old(request):
    use_db = "django_db_setup" in request.fixturenames
    gym_factory = request.getfixturevalue("gym_factory")

    def create(**kwargs):
        # kwargs = nest_dicts(kwargs)
        gym = kwargs.pop("gym", {})
        if isinstance(gym, dict):
            gym = gym_factory(**gym)

        defaults = {
            "gym": gym,
            "start": "10:00",
            "end": "11:00",
            "phone_number": "+491234567890",
        }

        if use_db:
            return Booking.objects.create(**{**defaults, **kwargs})
        return Booking(**{**defaults, **kwargs})

    return create


def create_booking(client, gym, date, start, end, phone_number):
    booking_url = reverse("booking-create", kwargs={"gym": gym.slug})
    return client.post(
        booking_url,
        {"date": date, "start": start, "end": end, "phone_no": phone_number},
        follow=True,
    )


def try_to_verify(client, booking, pin):
    verification_url = reverse("booking-verification", kwargs={"booking": booking.name})
    return client.post(verification_url, {"booking": booking.name, "pin": pin})
