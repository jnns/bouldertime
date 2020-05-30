from collections import defaultdict
from datetime import time, timedelta

from django.db import connection, models
from django.utils.functional import cached_property
from django.utils.timezone import localdate
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
    address = models.CharField(verbose_name=_("Address"), blank=True, max_length=255)
    opens_at = models.TimeField(default=at_10am, verbose_name=_("Opens at"))
    closes_at = models.TimeField(default=at_10pm, verbose_name=_("Closes at"))
    max_guests = models.PositiveSmallIntegerField(
        default=100,
        help_text=_(
            "Maximum number of people that are allowed to occupy the space simultaneously. "
            "Also the maximum number of bookings for a time slot."
        ),
    )
    num_days_available = models.PositiveSmallIntegerField(
        default=3,
        verbose_name=_("Bookable days"),
        help_text=_(
            "How many days can be booked in advance? "
            "How many days are shown on the booking overview?"
        ),
    )

    def __str__(self):
        return self.name

    @cached_property
    def attendance(self):
        assert self.opens_at.hour
        assert self.closes_at.hour
        assert self.max_guests
        with connection.cursor() as cursor:
            cursor.execute(
                """
                with date as (
                 select date::date from generate_series(
                  current_date,
                  current_date + interval '%s days',
                  interval '1 day'
                ) as date),

                hours as (
                  select make_time(s.h, 0,0) as hour from generate_series(%s, %s) as s(h)
                )

                select
                  d.date,
                  date_part('hour', hours.hour) as hour,
                  ceil(
                    count(hour) filter (
                      where b.status in ('NEW', 'CONFIRMED')
                      and (d.date + hours.hour, d.date + hours.hour) overlaps (b.date + b.start, b.date + b.end)
                    )::numeric / %s * 100
                  ) as booking_count
                from hours
                left outer join core_booking b on (1=1)
                left outer join date d on (1=1)
                group by d.date, hour order by d.date, hour;
                """,
                (
                    self.num_days_available - 1,
                    self.opens_at.hour,
                    self.closes_at.hour - 1,
                    self.max_guests,
                ),
            )
            attendance = defaultdict(dict)
            for date, hour, num_bookings in cursor.fetchall():
                attendance[str(date)][int(hour)] = int(num_bookings)
            return attendance

    def is_available(self, date, hour):
        try:
            return self.attendance[str(date)][hour] < 100
        except KeyError:
            return False

    def get_available_end_hours(self, date, hour):
        end_hours = []
        max_bookable_hours = 3
        for i in range(max_bookable_hours):
            checked_hour = hour + i
            end_hour = checked_hour + 1
            if self.is_available(date, checked_hour):
                end_hours.append(end_hour)
            else:
                break
        return end_hours

    def get_opening_hours(self):
        return range(self.opens_at.hour, self.closes_at.hour)

    def get_bookables(self):
        bookables = defaultdict(dict)
        next_days = [
            localdate() + timedelta(days=i) for i in range(self.num_days_available)
        ]
        for date in next_days:
            for hour in self.get_opening_hours():
                bookables[str(date)][hour] = list(
                    self.get_available_end_hours(date, hour)
                )
        return bookables
