#import sys
from bs4 import BeautifulSoup
import requests
import re
import pandas as pd

log = open("log.txt", "w")
nicknames = {
    'umbc': 'maryland-baltimore-county',
    'ucf': 'central-florida',
    'unlv': 'nevada-las-vegas'
}

class Game:
    def __init__(self, winner, loser, link):
        self.winner = winner
        self.loser = loser
        self.link = link

def getGames(month, day, year):
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
            if ch in loser: winner = winner.replace(ch, '')
        if len(winnerTag) > 1:
            link = "https://www.sports-reference.com" + winnerTag[1]['href'].encode('utf-8')
        else:
            link = "https://www.sports-reference.com" + loserTag[1]['href'].encode('utf-8')
        allObjects.append(
            Game(
                winner,
                loser,
                link
            )
        )
    return allObjects
    
def getBox(html, team):
    global log
    
    if team in nicknames: team = nicknames[team]
    
    print 'box-score-basic-' + team
    test = html.find('table', id='box-score-basic-' + team)
    
    try:
        test.select("thead th")
    except AttributeError:
        log.write("ERROR: " + team + " is an incorrect team name" + '\n')
        return
    
    headers = test.select("thead th")
    headers = headers[2:]
    colHeads = []
    for h in headers: colHeads.append(h.get_text())
    colHeads = [h.encode("utf-8") for h in colHeads]
    colHeads[0] = 'Name'
    df = pd.DataFrame(columns=colHeads)   
    rows = test.select("tbody tr")
    rows.remove(rows[5])
    for row in rows:
        line = []
        name = row.select("th")[0].get_text().encode('utf-8')
        line.append(name)
        data = row.select('td')
        for x in data:
            line.append(x.get_text().encode("utf-8"))
        series = pd.Series(line,colHeads)
        df = df.append([series], ignore_index=True)       
    df.to_csv("csv/" + team + ".csv")
    
def processGame(game):
    page = requests.get(game.link)
    html = BeautifulSoup(page.content, 'html.parser')
    getBox(html, game.winner)
    getBox(html, game.loser)

def main():
    global log
    games = getGames("11", "24", "2017")
    for game in games:
        processGame(game)
    log.close()
        
if __name__ == "__main__": main()
                