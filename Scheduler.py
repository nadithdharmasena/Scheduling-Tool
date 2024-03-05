import logging

import datetime_utils
import scheduling_utils

from PermitDB import PermitDB
from Team import Team
from WeeklySchedule import WeeklySchedule
from Permit import Permit
from CommuteTimeCalculator import CommuteTimeCalculator
from Constants import Constants

from typing import List, Tuple
from datetime import timedelta, date, datetime, time


class Scheduler:
    def __init__(self):
        pass

    @staticmethod
    def schedule_round_robin(schedule_name: str, teams: List[Team], permit_db: PermitDB, start_date, end_date):

        schedule = WeeklySchedule(schedule_name, start_date, end_date, 2)

        unbalanced_matchups = scheduling_utils.generate_unbalanced_matchups(teams)
        matchups: List[Tuple[Team, Team]] = \
            scheduling_utils.generate_balanced_matchups(unbalanced_matchups, teams)

        matchups = scheduling_utils.shuffle_matchups(matchups)

        remaining_matchups = Scheduler._schedule(schedule, matchups, permit_db, start_date, end_date)

        return schedule, remaining_matchups

    @staticmethod
    def schedule_double_round_robin(schedule_name: str, teams: List[Team], permit_db: PermitDB, start_date, end_date):
        def duplicate_elements(original_list):
            ret_list = []
            for element in original_list:
                ret_list.append(element)
                ret_list.append((element[1], element[0]))
            return ret_list

        schedule = WeeklySchedule(schedule_name, start_date, end_date, 2)
        unbalanced_matchups = scheduling_utils.generate_unbalanced_matchups(teams)

        matchups: List[Tuple[Team, Team]] = \
            scheduling_utils.generate_balanced_matchups(unbalanced_matchups, teams)

        matchups = duplicate_elements(matchups)
        matchups = scheduling_utils.shuffle_matchups(matchups)

        remaining_matchups = Scheduler._schedule(schedule, matchups, permit_db, start_date, end_date)

        return schedule, remaining_matchups

    @staticmethod
    def _schedule(schedule: WeeklySchedule,
                  matchups: List[Tuple[Team, Team]],
                  permit_db: PermitDB,
                  start_date,
                  end_date):

        def compare_tuples_with_priority(time1, time2) -> bool:
            if time1[0] == time2[0]:
                return time1[1] <= time2[1]
            return time1[0] < time2[0]

        ctc = CommuteTimeCalculator.instance()
        num_expected_matchups = len(matchups)
        unscheduled_matchups = []

        for matchup in matchups:
            # We want to minimize travel time for the home team
            home_team: Team = matchup[0]
            away_team: Team = matchup[1]

            optimal_permit_for_matchup = None
            optimal_permit_scheduling_interval = None
            optimal_permit_home_team_commute_times: Tuple[int, int] = (1000, 1000)

            current_date: date = start_date
            while current_date <= end_date:
                current_dt = datetime.combine(current_date, time())
                permits_for_date = permit_db.get_permits_for_date(current_date)

                for permit in permits_for_date:

                    # Disregards unavailable or undersized permits
                    if not permit.is_available() or permit.size != 'L':
                        continue

                    teams_available_interval = Team.get_overlapping_availability(home_team, away_team, current_dt)
                    scheduling_interval = datetime_utils.find_intersection_of_dt_intervals(
                        teams_available_interval, permit.get_availability_interval())

                    eligibility_criteria = [
                        not home_team.is_strictly_unavailable(current_dt),
                        not away_team.is_strictly_unavailable(current_dt),
                        schedule.is_team_under_playing_caps_for_date(home_team, current_dt),
                        schedule.is_team_under_playing_caps_for_date(away_team, current_dt),
                        datetime_utils.length_of_interval_in_hours(scheduling_interval) >= Constants.game_length
                    ]

                    if all(eligibility_criteria):
                        home_team_commute_minutes = ctc.get_commute_time(home_team.address,
                                                                         permit.map_location,
                                                                         'driving',
                                                                         scheduling_interval[0])

                        away_team_commute_minutes = ctc.get_commute_time(away_team.address,
                                                                         permit.map_location,
                                                                         'driving',
                                                                         scheduling_interval[0])

                        proposed_commute_times = (home_team_commute_minutes, away_team_commute_minutes)

                        if optimal_permit_for_matchup is None or \
                            (optimal_permit_for_matchup and
                             compare_tuples_with_priority(proposed_commute_times,
                                                          optimal_permit_home_team_commute_times)):

                            optimal_permit_for_matchup = permit
                            optimal_permit_scheduling_interval = scheduling_interval
                            optimal_permit_home_team_commute_times = proposed_commute_times

                current_date += timedelta(days=1)

            if optimal_permit_for_matchup is None:
                unscheduled_matchups.append(matchup)
            else:
                permit_for_reservation = permit_db.get_permit_for_reservation(optimal_permit_for_matchup,
                                                                              optimal_permit_scheduling_interval)
                game = schedule.schedule_matchup(matchup[0], matchup[1], permit_for_reservation)
                permit_for_reservation.reserve(game)

        logging.info(f"{schedule.name} | Scheduled {schedule.get_num_games()} out of {num_expected_matchups} "
                     f"expected -- {len(unscheduled_matchups)} left: {unscheduled_matchups}")

        return unscheduled_matchups
