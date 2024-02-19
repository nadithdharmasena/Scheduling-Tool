from datetime import datetime, timedelta
import calendar


def extract_time(time_string):
    # Parse the string to datetime object using the correct format
    time_obj = datetime.strptime(time_string, '%I:%M %p')
    # Extract the time part and return
    return time_obj.time()


def parse_date_with_current_year(date_str):
    # Parse the date string into a date object without considering the year
    parsed_date = datetime.strptime(date_str, "%a, %b %d")

    # Get the current year
    current_year = datetime.now().year

    # Replace the year in the parsed date with the current year
    date_with_current_year = parsed_date.replace(year=current_year)

    return date_with_current_year.date()


def parse_date_range_string(date_range_string, year):
    ret_dates = []

    start_date_str, end_date_str = date_range_string.split('-')
    start_date_str = start_date_str.strip()
    end_date_str = end_date_str.strip()

    start_date = datetime.strptime(f'{start_date_str}/{year}', '%m/%d/%Y')
    end_date = datetime.strptime(f'{end_date_str}/{year}', '%m/%d/%Y')
    delta = end_date - start_date

    for i in range(delta.days + 1):
        ret_dates.append(start_date + timedelta(days=i))

    return ret_dates


def parse_month_string(month_string, year, month_to_num):
    ret_dates = []

    month_name = next((month for month in month_to_num if month in month_string), None)
    if month_name:
        month_num = month_to_num[month_name]
        last_day = calendar.monthrange(year, month_num)[1]
        for day in range(1, last_day + 1):
            ret_dates.append(datetime(year, month_num, day))

    return ret_dates


def parse_list_of_date_intervals_string(date_string, year=None):
    if year is None:
        year = datetime.now().year  # Use the current year if none specified

    if date_string == "-":
        return []

    # Month name to number mapping
    month_to_num = {month: index for index, month in enumerate(calendar.month_name) if month}

    dates = [component.strip() for component in date_string.split(';')]
    parsed_dates = []

    for date in dates:
        if '-' in date:
            # Handle date range
            parsed_dates.extend(parse_date_range_string(date, year))
        elif any(month in date for month in month_to_num):
            # Handle entire month
            parsed_dates.extend(parse_month_string(date, year, month_to_num))
        else:
            # Handle single date
            parsed_date = datetime.strptime(f'{date}/{year}', '%m/%d/%Y')
            parsed_dates.append(parsed_date)

    return parsed_dates


def parse_time_interval(time_str):

    if time_str == "-":
        return None

    # Split the string into start and end times
    start_str, end_str = time_str.split('-')

    # Format to parse the times
    time_format = '%I:%M%p' if ':' in start_str else '%I%p'
    end_format = '%I:%M%p' if ':' in end_str else '%I%p'

    # Parse the start and end times into datetime objects to extract time components
    start_time = datetime.strptime(start_str, time_format).time()
    end_time = datetime.strptime(end_str, end_format).time()

    return start_time, end_time


def test_date_parsers():
    # Example usage
    date_string = "March; 4/29; 5/6 - 5/10"
    # Assuming the current year, or you can specify any year e.g., year=2023
    parsed_dates = parse_list_of_date_intervals_string(date_string)

    for date in parsed_dates:
        print(date.strftime('%Y-%m-%d'))


def test_time_parsers():
    # Example usage:
    time_interval = "4pm-4:30pm"
    start_time, end_time = parse_time_interval(time_interval)
    print("Start time:", start_time, "End time:", end_time)

    time_interval = "10am-2pm"
    start_time, end_time = parse_time_interval(time_interval)
    print("Start time:", start_time, "End time:", end_time)

