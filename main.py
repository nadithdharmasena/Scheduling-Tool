from Team import Team
from DailyAvailability import DailyAvailability
from PermitDB import PermitDB
from Permit import Permit
from Scheduler import Scheduler

from datetime import datetime, date

import parsers
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
        availability = [DailyAvailability(interval) for interval in avail_intervals]
        blackout_dates = parsers.parse_list_of_date_intervals_string(complete_exclusion_list)

        new_team = Team(team_name, "", availability, blackout_dates)

        teams.append(new_team)

    return teams


def create_permit_db_from_file(file_path):

    permit_db = PermitDB()

    df = pd.read_csv(file_path, skiprows=4)
    df_cleaned = df.dropna(subset=["Park", "Field", "Size", "Date", "StartTime", "EndTime"])

    # Iterate through each row in the DataFrame
    for index, row in df_cleaned.iterrows():
        name = str(row['Park'])
        field = str(row['Field'])
        size = str(row['Size'])

        date_str = str(row['Date'])
        start_time_str = str(row['StartTime'])
        end_time_str = str(row['EndTime'])

        active_date = parsers.parse_date_with_current_year(date_str)
        start_time = parsers.extract_time(start_time_str)
        end_time = parsers.extract_time(end_time_str)

        start_time_dt = datetime.combine(active_date, start_time)
        end_time_dt = datetime.combine(active_date, end_time)

        if size == "L" or size == "XL":
            new_permit = Permit(name, field, size, start_time_dt, end_time_dt)
            permit_db.add_permit(new_permit, active_date)

    return permit_db


def main():

    teams = extract_teams_from_file('team_info.csv')
    permit_db = create_permit_db_from_file('permits.csv')

    season_start_date = date(2024, 3, 11)
    season_end_date = date(2024, 5, 10)

    Scheduler.schedule_round_robin(teams, permit_db, season_start_date, season_end_date)


main()