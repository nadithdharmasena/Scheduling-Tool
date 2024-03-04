import os
import googlemaps
import logging

from typing import Dict, Tuple


class CommuteTimeCalculator:

    hits = 1

    def __init__(self):
        self._gmaps_api_key = os.getenv('GMAPS_API_KEY')

        if self._gmaps_api_key is None:
            exit("GMAPS_API_KEY unset")

        self.gmaps = googlemaps.Client(key=self._gmaps_api_key)
        self._cache: Dict[Tuple[str, str], int] = dict()

    def get_commute_time(self, origin, destination, mode, arrival_dt):

        # Function to convert duration to minutes
        def convert_duration_to_minutes(duration_str):
            time_parts = duration_str.split()
            minutes = 0
            for i in range(0, len(time_parts), 2):
                if time_parts[i + 1].startswith('hour'):
                    minutes += int(time_parts[i]) * 60
                elif time_parts[i + 1].startswith('min'):
                    minutes += int(time_parts[i])
            return minutes

        duration_in_minutes = 0

        cache_key = (origin, destination)
        if cache_key in self._cache:
            logging.info(f"Cache Hit: {cache_key}")

            duration_in_minutes = self._cache[cache_key]
        else:
            CommuteTimeCalculator.hits += 1
            logging.info(f"Cache Miss -- fetching from Google ({CommuteTimeCalculator.hits}): {cache_key}")

            try:

                if CommuteTimeCalculator.hits > 0:
                    raise Exception("Too many API calls")

                distance_result = self.gmaps.distance_matrix(origins=origin,
                                                             destinations=destination,
                                                             mode=mode,
                                                             arrival_time=arrival_dt)

                # Extracting duration and converting it to minutes
                duration = distance_result['rows'][0]['elements'][0]['duration']['text']
                duration_in_minutes = convert_duration_to_minutes(duration)
            except Exception as e:
                logging.error(e)

                # Set duration to value so large the permit cannot be used
                duration_in_minutes = 1000

        return duration_in_minutes

