import datetime_utils
import scheduling_utils

from PermitDB import PermitDB
from Team import Team
from WeeklySchedule import WeeklySchedule
from Permit import Permit
from CommuteTimeCalculator import CommuteTimeCalculator

from typing import List, Tuple
from datetime import timedelta, date, datetime, time


class Scheduler:
    def __init__(self):
        pass

    @staticmethod
    def schedule_round_robin(schedule_name: str, teams: List[Team], permit_db: PermitDB, start_date, end_date):

        schedule = WeeklySchedule(schedule_name, start_date, end_date, 2)
        ctc = CommuteTimeCalculator()
        matchups: List[Tuple[Team, Team]] = scheduling_utils.generate_balanced_and_randomized_matchups(teams)

        current_date: date = start_date
        while current_date <= end_date:
            current_dt = datetime.combine(current_date, time())
            permits_for_date = permit_db.get_permits_for_date(current_date)

            permit_index = 0

            while permit_index < len(permits_for_date):
                permit: Permit = permits_for_date[permit_index]

                if not permit.is_available():
                    permit_index += 1
                    continue

                optimal_matchup = None
                optimal_matchup_scheduling_interval = (None, None)
                remaining_matchups = []
                for matchup_idx, matchup in enumerate(matchups):
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

                    if all(eligibility_criteria) and optimal_matchup is None:
                        # This is an eligible matchup for the given permit
                        home_team_commute_minutes = ctc.get_commute_time(home_team.address,
                                                                         permit.address,
                                                                         'transit',
                                                                         scheduling_interval[0])

                        away_team_commute_minutes = ctc.get_commute_time(away_team.address,
                                                                         permit.address,
                                                                         'transit',
                                                                         scheduling_interval[0])

                        if home_team_commute_minutes <= 20 and away_team_commute_minutes <= 50:
                            optimal_matchup = matchup
                            optimal_matchup_scheduling_interval = scheduling_interval

                            remaining_matchups.extend(matchups[matchup_idx + 1:])
                            break
                        else:
                            remaining_matchups.append(matchup)

                    else:
                        remaining_matchups.append(matchup)

                if optimal_matchup is None:
                    # Signifies not a single matchup could use this permit
                    permit_index += 1
                else:
                    permit_for_reservation = permit_db.get_permit_for_reservation(permit,
                                                                                  optimal_matchup_scheduling_interval)
                    permit_for_reservation.reserve()
                    schedule.schedule_matchup(optimal_matchup[0], optimal_matchup[1], permit_for_reservation)

                matchups = remaining_matchups
                permits_for_date = permit_db.get_permits_for_date(current_date)

            current_date += timedelta(days=1)

        return schedule
