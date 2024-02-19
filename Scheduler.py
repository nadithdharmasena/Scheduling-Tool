from PermitDB import PermitDB
from Team import Team
from WeeklySchedule import WeeklySchedule

import itertools
import random

from typing import List, Tuple
from datetime import datetime, timedelta


class Scheduler:
    def __init__(self):
        pass

    @staticmethod
    def schedule_round_robin(schedule_name: str, teams: List[Team], permit_db: PermitDB, start_date, end_date):

        def randomize_tuple_elements(tuple_list):
            randomized_list = []
            for tup in tuple_list:
                if random.choice([True, False]):
                    randomized_list.append(tup)  # Keep the order
                else:
                    randomized_list.append((tup[1], tup[0]))  # Swap the order
            return randomized_list

        schedule = WeeklySchedule(schedule_name, start_date, end_date, 2)

        matchups: List[Tuple[Team, Team]] = list(itertools.combinations(teams, 2))
        matchups = randomize_tuple_elements(matchups)

        current_date = start_date
        while current_date <= end_date:
            remaining_matchups = []
            for matchup in matchups:
                permits_for_date = permit_db.get_permits_for_date(current_date)
                scheduled = False
                for permit in permits_for_date:
                    permit_start_dt = permit.start_dt

                    scheduling_criteria = [
                        matchup[0].is_available(permit_start_dt),
                        matchup[1].is_available(permit_start_dt),
                        schedule.is_team_under_playing_caps_for_date(matchup[0], permit.start_dt),
                        schedule.is_team_under_playing_caps_for_date(matchup[1], permit.start_dt)
                    ]

                    if all(scheduling_criteria):
                        permit_db.reserve_permit_slot(current_date, permit)
                        schedule.schedule_matchup(matchup[0], matchup[1], permit)
                        scheduled = True
                        break

                if not scheduled:
                    remaining_matchups.append(matchup)

            matchups = remaining_matchups
            current_date += timedelta(days=1)

        return schedule
