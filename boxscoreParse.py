#import sys
from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import argparse
import datetime

log = open("log.txt", "w")
nicknames = {
    'umbc': 'maryland-baltimore-county',
    'ucf': 'central-florida',
    'unlv': 'nevada-las-vegas'
}

def parseArgs():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-d', dest='date')
    return parser.parse_args()

class Game:
    def __init__(self, home, away, link):
        self.home = home
        self.away = away
        self.link = link

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
            winner = search.group(1)
        except:
            winner = winnerTag[0].get_text().replace(' ', '-').lower()
        try:
            loserLink = loserTag[0]['href'].encode('utf-8')
            search = re.search(regex, loserLink)
            loser = search.group(1)
        except:
            loser = loserTag[0].get_text().replace(' ', '-').lower()

        for ch in ['\'', '(', ')']:
            if ch in winner: winner = winner.replace(ch, '')
            if ch in loser: loser = loser.replace(ch, '')
        if len(winnerTag) > 1:
            link = "https://www.sports-reference.com" + winnerTag[1]['href'].encode('utf-8')
            home = winner
            away = loser
        else:
            link = "https://www.sports-reference.com" + loserTag[1]['href'].encode('utf-8')
            home = loser
            away = winner
        allObjects.append(
            Game(
                home,
                away,
                link
            )
        )
    return allObjects
    
def getBox(html, team, date):
    global log
    
    if team in nicknames: team = nicknames[team]
    
    test = html.find('table', id='box-score-basic-' + team)
    
    try:
        test.select("thead th")
    except AttributeError:
        log.write("ERROR: " + team + " is an incorrect team name" + '\n')
        return
    
    headers = test.select("thead th")
    headers = headers[2:]
    colHeads = ['Date']
    for h in headers: colHeads.append(h.get_text())
    colHeads = [h.encode("utf-8") for h in colHeads]
    colHeads[1] = 'Name'
    for percent in ['FG%', '2P%', '3P%', 'FT%']: colHeads.remove(percent)
    df = pd.DataFrame(columns=colHeads)   
    rows = test.select("tbody tr")
    rows.remove(rows[5])
    for row in rows:
        line = []
        name = row.select("th")[0].get_text().encode('utf-8')
        line = [datetime.datetime.strptime(date, "%Y-%m-%d").date(),name]
        data = row.select('td')
        for x in data:
            if not '_pct' in x['data-stat']:
                line.append(x.get_text().encode("utf-8"))
        series = pd.Series(line,colHeads)
        df = df.append([series], ignore_index=True)       
    df.to_csv("csv/" + team + ".csv")
    
def processGame(game, date):
    page = requests.get(game.link)
    html = BeautifulSoup(page.content, 'html.parser')
    getBox(html, game.home, date)
    getBox(html, game.away, date)

def main():
    global log
    args = parseArgs()
    date = args.date
    games = getGames(date)
    for game in games:
        processGame(game, date)
    log.close()
        
if __name__ == "__main__": main()
                