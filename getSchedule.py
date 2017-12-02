#import sys
from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import argparse

log = open("log.txt", "w")

class Game:
    def __init__(self, home, away):
        self.home = home
        self.away = away
        
def parseArgs():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-d', dest='date')
    return parser.parse_args()

def getGames(date):
    year, month, day = date.split('-')
    url = "https://www.sports-reference.com/cbb/boxscores/index.cgi?month=" + month + "&day=" + day + "&year=" + year
    page = requests.get(url)
    scoreboard = BeautifulSoup(page.content, 'html.parser')
    schedule = scoreboard.find('div', id = 'games')
    games = scoreboard.find_all('table', class_='teams')
    allObjects = []
    regex = "/cbb/schools/(.*)/"
    for game in games:
        teams = game.find_all('a')
        homeTag = teams[0]
        awayTag = teams[1]
        try:
            homeLink = homeTag['href'].encode('utf-8')
            search = re.search(regex, homeLink)
            home = search.group(1)
        except:
            home = homeTag.get_text().replace(' ', '-').lower()
        try:
            awayLink = awayTag['href'].encode('utf-8')
            search = re.search(regex, awayLink)
            away = search.group(1)
        except:
            away = awayTag.get_text().replace(' ', '-').lower()

        for ch in ['\'', '(', ')']:
            if ch in home: home = home.replace(ch, '')
            if ch in away: away = away.replace(ch, '')

        allObjects.append(
            Game(
                home,
                away
            )
        )
    return allObjects

def main():
    global log
    args = parseArgs()
    date = args.date
    games = getGames(date)
    for game in games:
        print "Away: " + game.away
        print "Home: " + game.home
        print
    log.close()
        
if __name__ == "__main__": main()