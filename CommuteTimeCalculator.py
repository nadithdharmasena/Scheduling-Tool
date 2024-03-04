import os
import googlemaps


class CommuteTimeCalculator:

    hits = 1

    def __init__(self):
        self._gmaps_api_key = os.getenv('GMAPS_API_KEY')

        if self._gmaps_api_key is None:
            exit("GMAPS_API_KEY unset")

        self.gmaps = googlemaps.Client(key=self._gmaps_api_key)

    def get_commute_time(self, origin, destination, mode, arrival_dt):

        # Function to convert duration to minutes
        def convert_duration_to_minutes(duration):
            time_parts = duration.split()
            minutes = 0
            for i in range(0, len(time_parts), 2):
                if time_parts[i + 1].startswith('hour'):
                    minutes += int(time_parts[i]) * 60
                elif time_parts[i + 1].startswith('min'):
                    minutes += int(time_parts[i])
            return minutes

        # Convert datetime to a Unix timestamp (seconds since epoch)
        arrival_timestamp = int(arrival_dt.timestamp())

        duration_in_minutes = 20

        CommuteTimeCalculator.hits += 1

        # distance_result = self.gmaps.distance_matrix(origin,
        #                                              destination,
        #                                              mode=mode,
        #                                              arrival_time=arrival_timestamp)
        #
        # # Extracting duration and converting it to minutes
        # duration = distance_result['rows'][0]['elements'][0]['duration']['text']
        # duration_in_minutes = convert_duration_to_minutes(duration)

        return duration_in_minutes
