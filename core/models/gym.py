from datetime import time

from django.db import connection, models
from django.utils.translation import gettext_lazy as _


def at_10am():
    return time(10)


def at_10pm():
    return time(22)


class Gym(models.Model):
    name = models.CharField(verbose_name=_("Name"), max_length=255)
    slug = models.SlugField(
        verbose_name=_("Shortname"),
        allow_unicode=True,
        help_text=_("A short name that is used in URLs."),
    )
    opens_at = models.TimeField(default=at_10am, verbose_name=_("Opens at"))
    closes_at = models.TimeField(default=at_10pm, verbose_name=_("Closes at"))
    max_guests = models.PositiveSmallIntegerField(
        default=100,
        help_text=_(
            "Maximum number of people that are allowed to occupy the space simultaneously. "
            "Also the maximum number of bookings for a time slot."
        ),
    )

    def __str__(self):
        return self.name

    def get_attendance(self):
        assert self.opens_at.hour
        assert self.closes_at.hour
        assert self.max_guests
        with connection.cursor() as cursor:
            cursor.execute(
                """
                with hours as (
                    select make_time(s.h, 0,0) as hour from generate_series(%s, %s) as s(h)
                )
                select date_part('hour', hours.hour),
                  ceil(count(hour) filter (where (hours.hour, hours.hour) overlaps (b.start, b.end))::numeric / %s * 100)
                from core_booking b
                cross join hours
                group by hours.hour order by hour;
                """,
                (self.opens_at.hour, self.closes_at.hour - 1, self.max_guests),
            )
            return {
                int(hour): int(num_bookings) for hour, num_bookings in cursor.fetchall()
            }

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
