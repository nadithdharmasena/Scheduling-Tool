from datetime import time, datetime, timedelta


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

    def is_available(self, check_time):
        """
        Determines if a given time falls within the start and end time,
        considering a 15-minute buffer on both ends.

        Parameters:
        - check_time: datetime.time - The time to check against the availability period.

        Returns:
        - bool: True if the time is within the availability (including buffer), otherwise False.
        """

        if self.startTime is None or self.endTime is None:
            return False

        # Convert time objects to datetime objects for easy manipulation
        # Use an arbitrary date for all conversions
        arbitrary_date = datetime.now().date()
        start_datetime = datetime.combine(arbitrary_date, self.startTime) - timedelta(minutes=self.buffer)
        end_datetime = datetime.combine(arbitrary_date, self.endTime) + timedelta(minutes=self.buffer)
        check_datetime = datetime.combine(arbitrary_date, check_time)

        # Adjust for the situation where the interval crosses midnight
        if self.endTime < self.startTime:
            if self.startTime > check_time > self.endTime:
                check_datetime += timedelta(days=1)
            end_datetime += timedelta(days=1)

        return start_datetime <= check_datetime <= end_datetime
