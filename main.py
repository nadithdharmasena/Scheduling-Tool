from CommuteTimeCalculator import CommuteTimeCalculator
from Constants import Constants
from Game import Game
from Scheduler import Scheduler

import pandas_utils

from datetime import date


def print_execution_stats():
    print(f"Total API calls: {CommuteTimeCalculator.hits}")


def main():

    # Set start/end dates of season
    season_start_date = date(2024, 3, 11)
    season_end_date = date(2024, 5, 10)
    permit_db = pandas_utils.create_permit_db_from_file('permits/permits_2024.csv', Constants.min_permit_length)

    # Club GX division scheduling
    clubgx_teams = pandas_utils.extract_teams_from_file('team_info/clubgx.csv')
    clubgx_schedule, clubgx_remaining_matchups = Scheduler.schedule_double_round_robin(
        "Club GX Division",
        clubgx_teams,
        permit_db,
        season_start_date,
        season_end_date
    )

    # Club A division scheduling
    cluba_teams = pandas_utils.extract_teams_from_file('team_info/cluba.csv')
    cluba_schedule, cluba_remaining_matchups = Scheduler.schedule_round_robin(
        "Club A Division",
        cluba_teams,
        permit_db,
        season_start_date,
        season_end_date
    )

    # Club B division scheduling
    clubb_teams = pandas_utils.extract_teams_from_file('team_info/clubb.csv')
    clubb_schedule, clubb_remaining_matchups = Scheduler.schedule_round_robin(
        "Club B Division",
        clubb_teams,
        permit_db,
        season_start_date,
        season_end_date
    )

    # Interscholastic division scheduling
    interscholastic_teams = pandas_utils.extract_teams_from_file('team_info/interscholastic.csv')
    interscholastic_schedule, interscholastic_remaining_matchups = Scheduler.schedule_round_robin(
        "Interscholastic Division",
        interscholastic_teams,
        permit_db,
        season_start_date,
        season_end_date)

    # Dump permits
    pandas_utils.dump_permit_db_to_csv(permit_db)

    # Dump team schedules
    pandas_utils.dump_team_schedules_to_csv(clubgx_schedule,
                                            clubgx_teams,
                                            clubgx_remaining_matchups)
    pandas_utils.dump_team_schedules_to_csv(cluba_schedule,
                                            cluba_teams,
                                            cluba_remaining_matchups)
    pandas_utils.dump_team_schedules_to_csv(clubb_schedule,
                                            clubb_teams,
                                            clubb_remaining_matchups)
    pandas_utils.dump_team_schedules_to_csv(interscholastic_schedule,
                                            interscholastic_teams,
                                            interscholastic_remaining_matchups)

    # Dump weekly schedules
    pandas_utils.dump_weekly_schedule_to_csv(clubgx_schedule)
    pandas_utils.dump_weekly_schedule_to_csv(cluba_schedule)
    pandas_utils.dump_weekly_schedule_to_csv(clubb_schedule)
    pandas_utils.dump_weekly_schedule_to_csv(interscholastic_schedule)

    CommuteTimeCalculator.instance().freeze()

    print_execution_stats()


main()
