from django.contrib import admin

from .models import Booking, Gym, PhoneNumber

admin.site.register(Booking)
admin.site.register(Gym)
admin.site.register(PhoneNumber)
