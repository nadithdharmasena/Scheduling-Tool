from datetime import datetime, date, timedelta

import datetime_utils
from Constants import Constants
from Permit import Permit
from typing import Tuple


class PermitDB:
    def __init__(self, min_hours_of_permit_availability):
        self._permits_by_date = dict()
        self._min_hours_of_permit_availability = min_hours_of_permit_availability

    def total_num_of_available_permits(self):
        count = 0
        for avail_date in self._permits_by_date:
            for permit in self._permits_by_date[avail_date]:
                count += 1 if permit.is_available() else 0

        return count

    def add_permit(self, permit, active_date):

        permit_availability_hours = datetime_utils.length_of_interval_in_hours(permit.get_availability_interval())
        if permit_availability_hours < self._min_hours_of_permit_availability:
            return

        if active_date in self._permits_by_date:
            self._permits_by_date[active_date].append(permit)
        else:
            self._permits_by_date[active_date] = [permit]

    def get_permits_for_date(self, requested_date):
        if requested_date in self._permits_by_date:
            return self._permits_by_date[requested_date]
        return []

    def get_permit_for_reservation(self, permit: Permit, scheduling_interval: Tuple[datetime, datetime]):

        permit_date = permit.start_dt.date()

        # The following value must be entirely contained within the permit's availability interval
        reservation_interval = (scheduling_interval[0], scheduling_interval[0] + timedelta(hours=Constants.game_length))
        no_split_required = (reservation_interval == permit.get_availability_interval())

        if no_split_required:
            # No need to split the permit
            permit_for_reservation = permit
        else:
            # Need to split the permit

            # The above interval splits the original permit interval into two potentially empty intervals
            availability_of_left_permit_interval = (permit.start_dt, reservation_interval[0])
            availability_of_right_permit_interval = (reservation_interval[1], permit.end_dt)

            # Create new permit that spans the reservation_interval
            permit_for_reservation = Permit.permit_copy_with_new_availability_interval(permit, reservation_interval)

            new_permit_from_left: Permit = \
                Permit.permit_copy_with_new_availability_interval(permit, availability_of_left_permit_interval)

            new_permit_from_right = \
                Permit.permit_copy_with_new_availability_interval(permit, availability_of_right_permit_interval)

            self.add_permit(permit_for_reservation, permit_date)
            self.add_permit(new_permit_from_left, permit_date)
            self.add_permit(new_permit_from_right, permit_date)

            # Remove the original permit and add the new permits
            filtered_permits = [filtered_permit for filtered_permit in self._permits_by_date[permit_date] if
                                filtered_permit.permit_id != permit.permit_id]

            self._permits_by_date[permit_date] = filtered_permits

        return permit_for_reservation



