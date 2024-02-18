import datetime

import DailyAvailability


class Team:
    def __init__(self,
                 name,
                 address,
                 availabilities,
                 blackout_dates):

        self.name = name
        self.address = address

        self.availabilities: dict[str, DailyAvailability] = {
            "Sunday": availabilities[0],
            "Monday": availabilities[1],
            "Tuesday": availabilities[2],
            "Wednesday": availabilities[3],
            "Thursday": availabilities[4],
            "Friday": availabilities[5],
            "Saturday": availabilities[6]
        }

        self.blackout_dates = blackout_dates

    def _is_strictly_unavailable(self, dt):
        given_date = dt.date()

        for unavailable_date in self.blackout_dates:
            if unavailable_date.date() == given_date:
                return True
        return False

    def is_available(self, dt: datetime):

        day_of_week = dt.strftime('%A')
        availability = self.availabilities[day_of_week]

        return not self._is_strictly_unavailable(dt) and availability.is_available(dt.time())



