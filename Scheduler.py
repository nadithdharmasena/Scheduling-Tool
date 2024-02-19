from Game import Game
from PermitDB import PermitDB
from Team import Team

import itertools

from typing import List, Tuple, Dict
from datetime import datetime, timedelta


class Scheduler:
    def __init__(self):
        pass

    @staticmethod
    def schedule_round_robin(teams: List[Team], permit_db: PermitDB, start_date, end_date):
        games_by_team_by_week: Dict[str, Dict[int, Game]] = {}

        matchups: List[Tuple[Team, Team]] = list(itertools.combinations(teams, 2))

        current_date = start_date
        while current_date <= end_date:
            remaining_matchups = []
            for matchup in matchups:
                permits_for_date = permit_db.get_permits_for_date(current_date)
                scheduled = False
                for permit in permits_for_date:
                    permit_start_dt = permit.start_dt

                    scheduling_criteria = [
                        matchup[0].is_available(permit_start_dt),
                        matchup[1].is_available(permit_start_dt)
                    ]

                    if all(scheduling_criteria):
                        permit_db.reserve_permit_slot(current_date, permit)
                        scheduled = True
                        break

                if not scheduled:
                    remaining_matchups.append(matchup)

            matchups = remaining_matchups
            current_date += timedelta(days=1)

        print(f"{len(matchups)} left")

        """
        1. Starting with March 11th, we are going to go through every date until and including May 10th
        2. For each date, try to schedule as many matchups as possible, according to the following constraints
            a. Both teams of the match up are available
            b. Neither team has played more than 2 games in the week
            c. There is a permit available
        """
