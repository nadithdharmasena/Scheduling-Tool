from CommuteTimeCalculator import CommuteTimeCalculator
from Constants import Constants
from Team import Team
from DailyAvailability import DailyAvailability
from PermitDB import PermitDB
from Permit import Permit
from Scheduler import Scheduler
import parsers

from datetime import datetime, date

import pandas as pd


def extract_teams_from_file(file_path):

    teams = []

    # Read the CSV file into a DataFrame
    df = pd.read_csv(file_path)

    # Iterate through each row in the DataFrame
    for index, row in df.iterrows():

        # Extract strings from dataframe
        team_name = row['Team']
        division = row['Division']

        availability_str_list = [
            row['Sunday'],
            row['Monday'],
            row['Tuesday'],
            row['Wednesday'],
            row['Thursday'],
            row['Friday'],
            row['Saturday']
        ]

        spring_break = str(row['Spring Break'])
        special_unavailability = str(row['Special Unavailability'])

        if special_unavailability != "-":
            complete_exclusion_list = spring_break + "; " + special_unavailability
        else:
            complete_exclusion_list = spring_break

        # Process raw availability and unavailability data
        avail_intervals = [parsers.parse_time_interval(avail_str) for avail_str in availability_str_list]
        availability = [DailyAvailability.create_daily_availability(interval) for interval in avail_intervals]
        blackout_dates = parsers.parse_list_of_date_intervals_string(complete_exclusion_list)

        new_team = Team(team_name, "", availability, blackout_dates)

        teams.append(new_team)

    return teams


def create_permit_db_from_file(file_path, min_hours_of_availability=2):

    permit_db = PermitDB(min_hours_of_availability)

    df = pd.read_csv(file_path, skiprows=4, dtype={"Permit #": str})
    df_cleaned = df.dropna(subset=["Park", "Field", "Size", "Date", "StartTime", "EndTime", "Permit #"])

    # Iterate through each row in the DataFrame
    for index, row in df_cleaned.iterrows():
        name = str(row['Park'])
        field = str(row['Field'])
        size = str(row['Size'])
        permit_number = str(row["Permit #"])

        date_str = str(row['Date'])
        start_time_str = str(row['StartTime'])
        end_time_str = str(row['EndTime'])

        active_date = parsers.parse_date_with_current_year(date_str)
        start_time = parsers.extract_time(start_time_str)
        end_time = parsers.extract_time(end_time_str)

        start_time_dt = datetime.combine(active_date, start_time)
        end_time_dt = datetime.combine(active_date, end_time)

        new_permits = Permit.generate_permits(name, field, size, start_time_dt, end_time_dt, permit_number)
        for permit in new_permits:
            permit_db.add_permit(permit, active_date)

    return permit_db


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
    permit_db = create_permit_db_from_file('permits/permits_2024.csv', Constants.game_length)

    # Club A division scheduling
    cluba_teams = extract_teams_from_file('team_info/cluba.csv')
    cluba_schedule = Scheduler.schedule_round_robin(
        "Club A Division Schedule",
        cluba_teams,
        permit_db,
        season_start_date,
        season_end_date
    )

    # Interscholastic division scheduling
    interscholastic_teams = extract_teams_from_file('team_info/interscholastic.csv')
    interscholastic_schedule = Scheduler.schedule_round_robin(
        "Interscholastic Division Schedule",
        interscholastic_teams,
        permit_db,
        season_start_date,
        season_end_date)

    # Club GX division scheduling
    clubgx_teams = extract_teams_from_file('team_info/clubgx.csv')
    clubgx_schedule = Scheduler.schedule_round_robin(
        "Club GX Division Schedule",
        clubgx_teams,
        permit_db,
        season_start_date,
        season_end_date
    )

    # Club B division scheduling
    clubb_teams = extract_teams_from_file('team_info/clubb.csv')
    clubb_schedule = Scheduler.schedule_round_robin(
        "Club B Division Schedule",
        clubb_teams,
        permit_db,
        season_start_date,
        season_end_date
    )

    # print_schedule_for_team(cluba_schedule, cluba_teams[0])


main()
print_execution_stats()
