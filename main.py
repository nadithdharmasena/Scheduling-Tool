from Team import Team
from DailyAvailability import DailyAvailability
import parsers
from datetime import datetime


def main():

    team_name = "Horace Mann"
    address = "123 Horace Mann Drive, New York, New York, 10017"

    avail_strs = ["-", "4pm-4:30pm", "-", "4pm-4:30pm", "-", "4pm-4:30pm", "10am-2pm"]
    avail_intervals = [parsers.parse_time_interval(avail_str) for avail_str in avail_strs]
    availabilities = [DailyAvailability(interval) for interval in avail_intervals]

    unavail_strs = "3/16 - 4/1; 3/1 - 3/15; 4/1; 4/9 - 4/10; 4/22 - 4/23"
    unavail_dts = parsers.parse_list_of_date_intervals_string(unavail_strs)

    my_team = Team(team_name, address, availabilities, unavail_dts)

    possible_dt = datetime(2024, 3, 2, 10, 30)

    print(my_team.is_available(possible_dt))


main()