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

            games_to_schedule: List[Tuple[Tuple[Team, Team], Permit]] = []

            for permit in permits_for_date:

                remaining_matchups = []

                # Finds all matchups that can be played using this permit
                eligible_matchups = []
                for matchup in matchups:
                    home_team = matchup[0]
                    away_team = matchup[1]

                    teams_available_interval = Team.get_overlapping_availability(home_team, away_team, current_dt)
                    scheduling_interval = datetime_utils.find_intersection_of_dt_intervals(
                        teams_available_interval, permit.get_availability_interval())

                    eligibility_criteria = [
                        home_team.is_strictly_unavailable(current_dt),
                        away_team.is_strictly_unavailable(current_dt),
                        schedule.is_team_under_playing_caps_for_date(home_team, current_dt),
                        schedule.is_team_under_playing_caps_for_date(away_team, current_dt),
                        datetime_utils.length_of_interval_in_hours(scheduling_interval) >= 2
                    ]

                    if all(eligibility_criteria):
                        eligible_matchups.append(matchup)
                    else:
                        # Matchups that definitely will not be scheduled using this permit
                        remaining_matchups.append(matchup)

                if len(eligible_matchups) > 0:
                    chosen_matchup = eligible_matchups[0]
                    games_to_schedule.append((chosen_matchup, permit))
                    remaining_matchups.extend(eligible_matchups[1:])

                matchups = remaining_matchups

            for game in games_to_schedule:
                matchup = game[0]
                permit = game[1]
                permit_db.reserve_permit_slot(current_dt, permit)
                schedule.schedule_matchup(matchup[0], matchup[1], permit)

            current_date += timedelta(days=1)

        return schedule
