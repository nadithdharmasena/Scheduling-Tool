from Game import Game
from Team import Team
from Permit import Permit

from datetime import datetime
from typing import Dict, List


class WeeklySchedule:
    def __init__(self, name, start_date, end_date, max_games_per_week):
        self.name: str = name
        self._start_date = start_date
        self._end_date = end_date
        self._max_games_per_week = max_games_per_week

        self._games_by_team_by_week: Dict[Team, Dict[int, List[Game]]] = dict()

    def is_team_under_playing_caps_for_date(self, team: Team, matchup_dt: datetime):
        which_week = matchup_dt.isocalendar()[1] - self._start_date.isocalendar()[1]

        # If the team has never played any teams in the given week, we know it must be under the weekly playing cap
        # So we do not need to check for the case in which the team or week does not already appear in the schedule
        if team in self._games_by_team_by_week:
            team_games_by_week = self._games_by_team_by_week[team]
            if which_week in team_games_by_week:
                team_games_for_given_week = team_games_by_week[which_week]

                # Now, verify that the team has not played a game on the proposed day
                for scheduled_game in team_games_for_given_week:
                    if scheduled_game.permit.start_dt.date() == matchup_dt.date():
                        return False

                return len(team_games_for_given_week) < self._max_games_per_week

        return True

    def schedule_matchup(self, home_team: Team, away_team: Team, permit: Permit):
        which_week = permit.start_dt.isocalendar()[1] - self._start_date.isocalendar()[1]
        new_game = Game(self.name, home_team, away_team, permit)

        self._add_game_for_team_in_week(new_game, home_team, which_week)
        self._add_game_for_team_in_week(new_game, away_team, which_week)

        return new_game

    def _add_game_for_team_in_week(self, game: Game, team: Team, which_week: int):

        if team not in self._games_by_team_by_week:
            self._games_by_team_by_week[team] = dict()

        if which_week not in self._games_by_team_by_week[team]:
            self._games_by_team_by_week[team][which_week] = []

        self._games_by_team_by_week[team][which_week].append(game)

    def get_schedule_for_team(self, team: Team):
        if team in self._games_by_team_by_week:
            return self._games_by_team_by_week[team]

        return dict()

    def get_games_for_week(self, requested_week):
        games = set()
        for games_for_team_by_week in self._games_by_team_by_week.values():
            for week, team_games_in_week in games_for_team_by_week.items():
                if week == requested_week:
                    games.update(team_games_in_week)

        return games
