from CommuteTimeCalculator import CommuteTimeCalculator
from Constants import Constants
from Scheduler import Scheduler

import pandas_utils

from datetime import date


def print_schedule_for_team(schedule, team):

    total_games = 0
    games_for_team = schedule.get_schedule_for_team(team)
    for week, game_list in games_for_team.items():
        print(f"Games in week #{week}")
        for index, game in enumerate(game_list):
            print(f"\t{index + 1}. {game}")
            total_games += 1

        print("=========================")

    return total_games


def print_games_per_week(schedule):
    total_games = 0
    for target_week in range(0, 10):
        print(f"Games in week #{target_week}:")

        games_in_week = schedule.get_games_for_week(target_week)
        total_games += len(games_in_week)
        for game in games_in_week:
            print(f"\t{game}")

    print(f"\nTotal number of games played: {total_games}")


def print_execution_stats():
    print(f"Total API calls: {CommuteTimeCalculator.hits}")


def main():

    # Set start/end dates of season
    season_start_date = date(2024, 3, 11)
    season_end_date = date(2024, 5, 10)
    permit_db = pandas_utils.create_permit_db_from_file('permits/permits_2024.csv', Constants.game_length)

    # Club A division scheduling
    cluba_teams = pandas_utils.extract_teams_from_file('team_info/cluba.csv')
    cluba_schedule = Scheduler.schedule_round_robin(
        "Club A Division Schedule",
        cluba_teams,
        permit_db,
        season_start_date,
        season_end_date
    )

    # Interscholastic division scheduling
    interscholastic_teams = pandas_utils.extract_teams_from_file('team_info/interscholastic.csv')
    interscholastic_schedule = Scheduler.schedule_round_robin(
        "Interscholastic Division Schedule",
        interscholastic_teams,
        permit_db,
        season_start_date,
        season_end_date)

    # Club GX division scheduling
    clubgx_teams = pandas_utils.extract_teams_from_file('team_info/clubgx.csv')
    clubgx_schedule = Scheduler.schedule_double_round_robin(
        "Club GX Division Schedule",
        clubgx_teams,
        permit_db,
        season_start_date,
        season_end_date
    )

    # Club B division scheduling
    clubb_teams = pandas_utils.extract_teams_from_file('team_info/clubb.csv')
    clubb_schedule = Scheduler.schedule_round_robin(
        "Club B Division Schedule",
        clubb_teams,
        permit_db,
        season_start_date,
        season_end_date
    )

    pandas_utils.dump_permit_db_to_csv(permit_db)


main()
print_execution_stats()
