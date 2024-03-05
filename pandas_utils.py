import logging

from Team import Team
from DailyAvailability import DailyAvailability
from PermitDB import PermitDB
from Permit import Permit
import parsers

from datetime import datetime
import pandas as pd

from WeeklySchedule import WeeklySchedule


def extract_teams_from_file(file_path):
    teams = []

    # Read the CSV file into a DataFrame
    df = pd.read_csv(file_path)

    # Iterate through each row in the DataFrame
    for index, row in df.iterrows():

        # Extract strings from dataframe
        team_name = row['Team']
        division = row['Division']
        address = row['Address']

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

        new_team = Team(team_name, address, availability, blackout_dates)

        teams.append(new_team)

    return teams


def create_permit_db_from_file(file_path, min_hours_of_availability=2):
    permit_db = PermitDB(min_hours_of_availability)

    df = pd.read_csv(file_path, skiprows=4, dtype={"Permit #": str, "Field Assigned to": str})
    df_cleaned = df.dropna(subset=["Park", "Field", "Size", "Date", "StartTime", "EndTime", "Permit #"])

    # Iterate through each row in the DataFrame
    for index, row in df_cleaned.iterrows():
        name = str(row['Park'])
        field = str(row['Field'])
        size = str(row['Size'])
        permit_number = str(row['Permit #'])
        borough = str(row['Borough'])
        map_location = str(row['Map Location'])

        date_str = str(row['Date'])
        start_time_str = str(row['StartTime'])
        end_time_str = str(row['EndTime'])

        # Ensures permits with prior commitments are not used
        field_assignment = row['Field Assigned to']
        if pd.isna(field_assignment):
            field_assignment = None

        active_date = parsers.parse_date_with_current_year(date_str)
        start_time = parsers.extract_time(start_time_str)
        end_time = parsers.extract_time(end_time_str)

        start_time_dt = datetime.combine(active_date, start_time)
        end_time_dt = datetime.combine(active_date, end_time)

        new_permits = Permit.generate_permits(name,
                                              field,
                                              size,
                                              start_time_dt,
                                              end_time_dt,
                                              permit_number,
                                              borough,
                                              map_location,
                                              field_assignment)
        for permit in new_permits:
            permit_db.add_permit(permit, active_date)

    return permit_db


def dump_permit_db_to_csv(permit_db):
    permits = permit_db.get_all_permits()
    filename = f"dumped_permits/dumped_permits.csv"

    # Prepare data for DataFrame
    data = {
        "Park": [permit.name for permit in permits],
        "Field": [permit.field for permit in permits],
        "Size": [permit.size for permit in permits],
        "Date": [permit.start_dt.strftime("%m/%d/%Y") for permit in permits],
        "StartTime": [permit.start_dt.strftime("%I:%M:%S %p") for permit in permits],
        "EndTime": [permit.end_dt.strftime("%I:%M:%S %p") for permit in permits],
        "Permit #": [permit.permit_number for permit in permits],
        "Borough": [permit.borough for permit in permits],
        "Map Location": [permit.map_location for permit in permits],
        "Field Assigned to": [permit.get_assignment() for permit in permits]
    }

    columns = ["Park",
               "Field",
               "Size",
               "",
               "",
               "",
               "Date",
               "",
               "StartTime",
               "EndTime",
               "Permit #",
               "",
               "",
               "",
               "",
               "",
               "",
               "Borough",
               "Map Location",
               "Field Assigned to"]

    # Create DataFrame with data and specified column headers, including empty ones for alignment
    df = pd.DataFrame(data, columns=columns)

    # Write DataFrame to CSV with the given filename
    df.to_csv(filename, index=False)


def dump_team_schedules_to_csv(schedule, teams, remaining_matchups):
    for team in teams:
        dump_team_schedule_to_csv(schedule, team)
        dump_remaining_matchups_to_csv(schedule, team, remaining_matchups)


def dump_team_schedule_to_csv(schedule, team):

    filedir = f"schedules/{schedule.name}"
    filename = f"{filedir}/{schedule.name}-{team.name}.csv"

    data = {
        "Week": [],
        "Date": [],
        "Home": [],
        "Away": [],
        "Start Time": [],
        "End Time": [],
        "Permit": [],
        "League Name": []
    }

    games_for_team = schedule.get_schedule_for_team(team)
    for week, game_list in games_for_team.items():
        for game in game_list:
            data["Week"].append(week)

            game_date_str = game.permit.start_dt.strftime('%m/%d/%Y')
            data["Date"].append(game_date_str)

            data["Home"].append(game.home_team)
            data["Away"].append(game.away_team)

            start_time_str = game.permit.start_dt.strftime('%I:%M %p')
            data["Start Time"].append(start_time_str)

            end_time_str = game.permit.end_dt.strftime('%I:%M %p')
            data["End Time"].append(end_time_str)

            data["Permit"].append(str(game.permit))
            data["League Name"].append(game.league_name)

    columns = ["Week", "Date", "Home", "Away", "Start Time", "End Time", "Permit", "League Name"]

    df = pd.DataFrame(data, columns=columns)

    df.to_csv(filename, index=False)


def dump_remaining_matchups_to_csv(schedule, team, remaining_matchups):
    filedir = f"schedules/{schedule.name}"
    filename = f"{filedir}/{schedule.name}-{team.name}-remainders.csv"

    data = {
        "Home": [matchup[0] for matchup in remaining_matchups if team in matchup],
        "Away": [matchup[1] for matchup in remaining_matchups if team in matchup],
        "League Name": [schedule.name for matchup in remaining_matchups if team in matchup]
    }

    columns = ["Home", "Away", "League Name"]

    df = pd.DataFrame(data, columns=columns)
    df.to_csv(filename, index=False)


def dump_weekly_schedule_to_csv(schedule: WeeklySchedule):
    filedir = f"schedules/{schedule.name}"
    filename = f"{filedir}/{schedule.name}-weekly.csv"

    data = {
        "Week": [],
        "Date": [],
        "Home": [],
        "Away": [],
        "Start Time": [],
        "End Time": [],
        "Permit": [],
        "League Name": []
    }

    all_games = schedule.get_all_games()
    for game in all_games:
        data["Week"].append(game.week)

        game_date_str = game.permit.start_dt.strftime('%m/%d/%Y')
        data["Date"].append(game_date_str)

        data["Home"].append(game.home_team)
        data["Away"].append(game.away_team)

        start_time_str = game.permit.start_dt.strftime('%I:%M %p')
        data["Start Time"].append(start_time_str)

        end_time_str = game.permit.end_dt.strftime('%I:%M %p')
        data["End Time"].append(end_time_str)

        data["Permit"].append(str(game.permit))
        data["League Name"].append(game.league_name)

    columns = ["Week", "Date", "Home", "Away", "Start Time", "End Time", "Permit", "League Name"]

    df = pd.DataFrame(data, columns=columns)
    df.to_csv(filename, index=False)


