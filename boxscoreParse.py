#import sys
from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import argparse
import datetime
from Objects import *

log = open("log.txt", "w")

def parseArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', dest='date')
    return parser.parse_args()

def getGames(date):
    year, month, day = date.split('-')
    url = "https://www.sports-reference.com/cbb/boxscores/index.cgi?month=" + month + "&day=" + day + "&year=" + year
    page = requests.get(url)
    scoreboard = BeautifulSoup(page.content, 'html.parser')
    games = scoreboard.find_all('div', class_= 'game_summary nohover')
    allObjects = []
    regex = "/cbb/schools/(.*)/"
    for game in games:
        winnerTag = game.find('tr', class_= 'winner').find_all('a')
        loserTag = game.find('tr', class_= 'loser').find_all('a')
        try:
            winnerLink = winnerTag[0]['href'].encode('utf-8')
            search = re.search(regex, winnerLink)
            winner = Team(search.group(1))
        except:
            winner = Team(winnerTag[0].get_text().replace(' ', '-').lower())
        try:
            loserLink = loserTag[0]['href'].encode('utf-8')
            search = re.search(regex, loserLink)
            loser = Team(search.group(1))
        except:
            loser = Team(loserTag[0].get_text().replace(' ', '-').lower())

        for ch in ['\'', '(', ')']:
            if ch in winner.name: winner.name = winner.name.replace(ch, '')
            if ch in loser.name: loser.name = loser.name.replace(ch, '')
        if len(winnerTag) > 1:
            link = "https://www.sports-reference.com" + winnerTag[1]['href'].encode('utf-8')
            home = winner
            away = loser
        else:
            link = "https://www.sports-reference.com" + loserTag[1]['href'].encode('utf-8')
            home = loser
            away = winner
        obj = Game(home,away)
        obj.link = link
        allObjects.append(obj)
    return allObjects
    
def getBox(html, game, date):
    global log
    
    teams = [game.home, game.away]
    
    for team in teams:
        test = html.find('table', id='box-score-basic-' + team.name)
        if team.isHome: opponent = game.away.name
        else: opponent = game.home.name
        try:
            test.select("thead th")
        except AttributeError:
            log.write("ERROR: " + team.name + " is an incorrect team name" + '\n')
            return
        
        headers = test.select("thead th")
        headers = headers[2:]
        colHeads = ['Date', 'Opponent']
        for h in headers: colHeads.append(h.get_text())
        colHeads = [h.encode("utf-8") for h in colHeads]
        colHeads[2] = 'Name'
        for percent in ['FG%', '2P%', '3P%', 'FT%']: colHeads.remove(percent)
        df = pd.DataFrame(columns=colHeads)   
        rows = test.select("tbody tr")
        rows.remove(rows[5])
        for row in rows:
            name = row.select("th")[0].get_text().encode('utf-8')
            line = [datetime.datetime.strptime(date, "%Y-%m-%d").date(), opponent, name]
            data = row.select('td')
            for x in data:
                if not '_pct' in x['data-stat']:
                    line.append(x.get_text().encode("utf-8"))
            series = pd.Series(line,colHeads)
            df = df.append([series], ignore_index=True)
        team.box = df
        #df.to_csv("csv/" + date + "-" + team.name + ".csv")
    return game
    
def processGame(game, date):
    page = requests.get(game.link)
    html = BeautifulSoup(page.content, 'html.parser')
    getBox(html, game, date)

def main():
    global log
    args = parseArgs()
    date = args.date
    games = getGames(date)
    for game in games:
        game = processGame(game, date)
    print(games[0].home.box)
    log.close()
        
if __name__ == "__main__": main()
                