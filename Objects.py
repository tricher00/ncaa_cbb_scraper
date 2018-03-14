class Game:
    def __init__(self, date, home, away):
        self.date = date
        self.home = home
        self.home.isHome = True
        self.away = away
        self.link = None
        self.homeScore = 0
        self.awayScore = 0
        
class Team:
    def __init__(self, name):
        self.name = name
        self.isHome = False
        self.box = None