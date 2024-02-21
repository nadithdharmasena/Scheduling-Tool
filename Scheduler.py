import datetime_utils
from PermitDB import PermitDB
from Team import Team
from WeeklySchedule import WeeklySchedule
from Permit import Permit

import itertools
import random

from typing import List, Tuple
from datetime import timedelta, date, datetime, time


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

        current_date: date = start_date
        while current_date <= end_date:
            current_dt = datetime.combine(current_date, time())
            permits_for_date = permit_db.get_permits_for_date(current_date)

            permit_index = 0

            while permit_index < len(permits_for_date):
                permit: Permit = permits_for_date[permit_index]

                optimal_matchup = None
                remaining_matchups = []
                for matchup in matchups:
                    home_team = matchup[0]
                    away_team = matchup[1]

                    teams_available_interval = Team.get_overlapping_availability(home_team, away_team, current_dt)
                    scheduling_interval = datetime_utils.find_intersection_of_dt_intervals(
                        teams_available_interval, permit.get_availability_interval())

                    eligibility_criteria = [
                        not home_team.is_strictly_unavailable(current_dt),
                        not away_team.is_strictly_unavailable(current_dt),
                        schedule.is_team_under_playing_caps_for_date(home_team, current_dt),
                        schedule.is_team_under_playing_caps_for_date(away_team, current_dt),
                        datetime_utils.length_of_interval_in_hours(scheduling_interval) >= 2
                    ]

                    if all(eligibility_criteria):
                        # This is an eligible matchup for the given permit
                        if optimal_matchup is not None:
                            remaining_matchups.append(optimal_matchup)
                        optimal_matchup = matchup
                    else:
                        remaining_matchups.append(matchup)

                if optimal_matchup is not None:
                    schedule.schedule_matchup(optimal_matchup[0], optimal_matchup[1], permit)
                    permit.reserve()

                permit_index += 1
                matchups = remaining_matchups

            current_date += timedelta(days=1)

        return schedule
