import datetime
import os
import googlemaps
import logging
import pickle

from typing import Dict, Tuple

from Constants import Constants

logging.basicConfig(level=logging.INFO)


class CommuteTimeCalculator:
    pickled_cache_fp = "pickles/ctc_cache.pk"
    ctc = None
    hits = 0

    def __init__(self, cache):
        self._gmaps_api_key = os.getenv('GMAPS_API_KEY')

        if self._gmaps_api_key is None:
            exit("GMAPS_API_KEY unset")

        self._gmaps = googlemaps.Client(key=self._gmaps_api_key)

        if cache:
            self._cache: Dict[Tuple[str, str], int] = cache
        else:
            self._cache: Dict[Tuple[str, str], int] = dict()

    @staticmethod
    def instance():

        if CommuteTimeCalculator.ctc:
            return CommuteTimeCalculator.ctc

        pickled_cache = None

        try:
            with open(CommuteTimeCalculator.pickled_cache_fp, 'rb') as file:
                pickled_cache = pickle.load(file)
        except FileNotFoundError as e:
            logging.error(e)
        except Exception as e:
            logging.error(e)

        CommuteTimeCalculator.ctc = CommuteTimeCalculator(pickled_cache)

        return CommuteTimeCalculator.ctc

    def freeze(self):
        with open(CommuteTimeCalculator.pickled_cache_fp, 'wb') as file:
            pickle.dump(self._cache, file)

    def get_commute_time(self, origin, destination, mode, arrival_dt):

        duration_in_minutes = 0

        # Hacky, special case because Google does not recognize Riverside Park as a single address
        if destination == "Riverside Park":
            destination = "Riverside Dr &, W 105th St, New York, NY 10025"

        cache_key = (origin, destination)
        if cache_key in self._cache:
            duration_in_minutes = self._cache[cache_key]
        else:
            CommuteTimeCalculator.hits += 1
            logging.info(f"Cache Miss -- fetching from Google ({CommuteTimeCalculator.hits}): {cache_key}")

            try:
                duration_in_minutes = self.get_commute_time_from_gmaps(origin, destination, mode, arrival_dt)
            except Exception as e:
                logging.error(e)

                # Set duration to value so large the permit cannot be used
                duration_in_minutes = 1000

        self._cache[cache_key] = duration_in_minutes

        return duration_in_minutes

    def get_commute_time_from_gmaps(self, origin, destination, mode, arrival_dt):

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

        distance_result = self._gmaps.distance_matrix(origins=origin,
                                                      destinations=destination,
                                                      mode=mode,
                                                      arrival_time=arrival_dt)

        # Extracting duration and converting it to minutes
        duration = distance_result['rows'][0]['elements'][0]['duration']['text']

        return convert_duration_to_minutes(duration)
