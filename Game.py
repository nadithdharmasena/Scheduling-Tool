

class Game:
    def __init__(self, home_team, away_team, permit):
        self.home_team = home_team
        self.away_team = away_team
        self.permit = permit

    def __repr__(self):
        return f"{self.away_team} at {self.home_team} ({self.permit})"



