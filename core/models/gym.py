from django.db import models
from django.utils.translation import gettext_lazy as _


class Gym(models.Model):
    name = models.CharField(verbose_name=_("Name"), max_length=255)
    slug = models.SlugField(
        verbose_name=_("Shortname"),
        allow_unicode=True,
        help_text=_("A short name that is used in URLs."),
    )
    opens_at = models.TimeField(verbose_name=_("Opens at"))
    closes_at = models.TimeField(verbose_name=_("Closes at"))

    def __str__(self):
        return self.name

    def get_attendance(self):
        return {hour: Gym.fake_attendance(hour) for hour in self.get_opening_hours()}

    @staticmethod
    def fake_attendance(hour):
        return 100 - 100 * (abs(16 - hour) / 8)

    def is_available(self, hour):
        try:
            return self.get_attendance()[hour] < 100
        except KeyError:
            return False

    def get_available_end_hours(self, hour):
        end_hours = []
        max_bookable_hours = 3
        for i in range(max_bookable_hours):
            checked_hour = hour + i
            end_hour = checked_hour + 1
            if self.is_available(checked_hour):
                end_hours.append(end_hour)
            else:
                break
        return end_hours

    def get_opening_hours(self):
        return range(self.opens_at.hour, self.closes_at.hour)

    def get_bookables(self):
        bookables = {}
        for hour in self.get_opening_hours():
            bookables[hour] = list(self.get_available_end_hours(hour))
        return bookables
