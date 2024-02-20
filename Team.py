from DailyAvailability import DailyAvailability

from datetime import date, datetime


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

    def is_strictly_unavailable(self, proposed_dt: datetime):
        proposed_date = proposed_dt.date()
        for unavailable_date in self.blackout_dates:
            if unavailable_date.date() == proposed_date:
                return True
        return False

    def get_availability_for(self, proposed_dt: datetime):
        day_of_week = proposed_dt.strftime('%A')
        return self._availabilities[day_of_week]

    @staticmethod
    def get_overlapping_availability(team1, team2, proposed_dt: datetime):
        team1_availability = team1.get_availability_for(proposed_dt)
        team2_availability = team2.get_availability_for(proposed_dt)

        return DailyAvailability.get_overlapping_availability(team1_availability, team2_availability, proposed_dt)







