import datetime

import DailyAvailability


class Team:
    def __init__(self,
                 name,
                 address,
                 availability,
                 blackout_dates):

        self.name = name
        self.address = address

        self.availabilities: dict[str, DailyAvailability] = {
            "Sunday": availability[0],
            "Monday": availability[1],
            "Tuesday": availability[2],
            "Wednesday": availability[3],
            "Thursday": availability[4],
            "Friday": availability[5],
            "Saturday": availability[6]
        }

        self.blackout_dates = blackout_dates

    def __repr__(self):
        return "{team_name}".format(team_name=self.name)

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



