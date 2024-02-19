from Permit import Permit

import pandas as pd

from parsers import parse_date_with_current_year, extract_time
from datetime import datetime


class PermitDB:
    def __init__(self):
        self._permits_by_date = dict()

    def add_permit(self, permit, active_date):
        if active_date in self._permits_by_date:
            self._permits_by_date[active_date].append(permit)
        else:
            self._permits_by_date[active_date] = [permit]

    def get_permits_for_date(self, requested_date):
        if requested_date in self._permits_by_date:
            return self._permits_by_date[requested_date]
        return []

    def reserve_permit_slot(self, requested_date, permit):
        permit.use_slot()

        permits_for_date = self._permits_by_date[requested_date]
        cleaned_permits_for_date = \
            [valid_permit for valid_permit in permits_for_date if valid_permit.is_available()]

        self._permits_by_date[requested_date] = cleaned_permits_for_date

    def total_num_of_available_slots(self):
        count = 0
        for avail_date in self._permits_by_date:
            for permit in self._permits_by_date[avail_date]:
                count += permit.get_slots_remaining()

        return count



