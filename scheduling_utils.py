import random
import itertools


def generate_unbalanced_matchups(teams):
    return list(itertools.combinations(teams, 2))


def generate_balanced_matchups(matchups, teams):

    # Count home and away games for each team
    num_home_games = {team: 0 for team in teams}
    num_away_games = {team: 0 for team in teams}

    for home, away in matchups:
        num_home_games[home] += 1
        num_away_games[away] += 1

    # Attempt to balance games
    for idx, (home, away) in enumerate(matchups):
        if num_home_games[home] - num_away_games[home] > 1 and \
                num_away_games[away] - num_home_games[away] > 1:

            # Swap home-away spots
            matchups[idx] = (away, home)
            num_home_games[home] -= 1
            num_away_games[home] += 1

            num_home_games[away] += 1
            num_away_games[away] -= 1

    return matchups


def shuffle_matchups(matchups):
    random.shuffle(matchups)
    return matchups

