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

        self._availabilities: dict[str, DailyAvailability] = {
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
        return f"{self.name}"

    def __hash__(self):
        return f"{self.name}".__hash__()

    def is_strictly_unavailable(self, dt):
        given_date = dt.date()

        for unavailable_date in self.blackout_dates:
            if unavailable_date.date() == given_date:
                return True
        return False

    def is_available(self, dt):
        return True

    def get_availability_for(self, day):
        return self._availabilities.get(day, __default=None)






