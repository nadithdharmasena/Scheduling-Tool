from datetime import datetime, timedelta

from typing import Tuple


def find_intersection_of_dt_intervals(interval1: Tuple[datetime, datetime], interval2: Tuple[datetime, datetime]):

    if interval1 is None or interval2 is None:
        return None

    (start_dt1, end_dt1) = interval1
    (start_dt2, end_dt2) = interval2

    intersection_start = max(start_dt1, start_dt2)
    intersection_end = min(end_dt1, end_dt2)

    if intersection_start >= intersection_end:
        return None

    return intersection_start, intersection_end


def length_of_interval_in_hours(interval):
    if interval is None:
        return 0

    delta: timedelta = interval[1] - interval[0]
    return delta.total_seconds() / 3600
