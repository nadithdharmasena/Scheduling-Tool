
class Game:

    current_id = 1

    def __init__(self, home_team, away_team, permit):
        self.home_team = home_team
        self.away_team = away_team
        self.permit = permit

        self.game_id = Game.current_id
        Game.current_id += 1

    def __repr__(self):
        return f"{self.away_team} at {self.home_team}"

    def __str__(self):
        return repr(self)

    def __hash__(self):
        return self.game_id





