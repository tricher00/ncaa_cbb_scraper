class Game:
    def __init__(self, home, away):
        self.home = home
        self.home.isHome = True
        self.away = away
        self.link = None
        
class Team:
    def __init__(self, name):
        self.name = name
        self.isHome = False
        self.box = None