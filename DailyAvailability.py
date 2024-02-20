import datetime_utils
from datetime import datetime


class DailyAvailability:
    def __init__(self, interval, buffer=10):
        """
        Initializes the DailyAvailability object with a start and end time.

        Parameters:
        - start_time: datetime.time - The start time of the availability period.
        - end_time: datetime.time - The end time of the availability period.
        """

        if interval:
            self.startTime = interval[0]
            self.endTime = interval[1]
        else:
            self.startTime = None
            self.endTime = None

        self.buffer = buffer

    @staticmethod
    def create_daily_availability(interval):
        if interval is None:
            return None

        return DailyAvailability(interval)

    @staticmethod
    def get_overlapping_availability(da1, da2, dt):
        if da1 is None or da2 is None:
            return None

        given_date = dt.date()

        da1_start_dt = datetime.combine(given_date, da1.startTime)
        da1_end_dt = datetime.combine(given_date, da1.endTime)

        da2_start_dt = datetime.combine(given_date, da2.startTime)
        da2_end_dt = datetime.combine(given_date, da2.endTime)

        da1_interval = (da1_start_dt, da1_end_dt)
        da2_interval = (da2_start_dt, da2_end_dt)

        return datetime_utils.find_intersection_of_dt_intervals(da1_interval, da2_interval)
