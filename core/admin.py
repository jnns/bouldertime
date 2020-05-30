from django.contrib import admin

from .models import Booking, Gym, PhoneNumber, User

admin.site.register(User)


class BookingAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "created_at",
        "status",
        "gym",
        "date",
        "start",
        "end",
    ]
    list_filter = [
        "gym",
        "status",
    ]
    list_editable = ["status"]
    actions = ["confirm", "revert_checkin"]
    date_hierarchy = "created_at"
    search_fields = ["name"]

    def revert_checkin(self, request, queryset):
        num_changed = queryset.update(checkin_at=None, checkout_at=None)
        self.message_user(request, f"Reverted check-in of {num_changed} bookings.")

    revert_checkin.short_description = "Revert check-in status"

    def confirm(self, request, queryset):
        num_changed = queryset.update(status=Booking.STATUS_CONFIRMED)
        self.message_user(request, f"Confirmed status of {num_changed} bookings.")


class PhoneNumberAdmin(admin.ModelAdmin):
    list_display = ["hashed_number", "verified_at", "blocked_due_to"]


admin.site.register(Booking, BookingAdmin)
admin.site.register(Gym)
admin.site.register(PhoneNumber, PhoneNumberAdmin)
