#import sys
from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import argparse
import datetime
from Objects import *
from sqlStuff import *

log = open("log.txt", "w")

def parseArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', dest='start')
    parser.add_argument('-e', dest='end')
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

        for ch in ['\'', '(', ')', '&', '.']:
            if ch in winner.name: winner.name = winner.name.replace(ch, '')
            if ch in loser.name: loser.name = loser.name.replace(ch, '')
        if '--' in winner.name: winner.name = winner.name.replace('--', '-')
        if '--' in loser.name: loser.name = loser.name.replace('--', '-')
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
    colHeads = []
    teams = [game.home, game.away]
    
    for team in teams:
        test = html.find('table', id='box-score-basic-' + team.name)
        if team.isHome: 
            opponent = game.away.name
            location = 'Home'
        else: 
            opponent = game.home.name
            location = 'Away'
        try:
            test.select("thead th")
        except AttributeError:
            log.write("ERROR: " + team.name + " is an incorrect team name" + '\n')
            continue
        
        headers = test.select("thead th")
        headers = headers[2:]
        colHeads = ['Date', 'Team', 'Opponent', 'Location']
        for h in headers: colHeads.append(h.get_text())
        colHeads = [h.encode("utf-8") for h in colHeads]
        colHeads[4] = 'Name'
        colHeads.append('Coolness')
        for percent in ['FG%', '2P%', '3P%', 'FT%']: colHeads.remove(percent)
        df = pd.DataFrame(columns=colHeads)   
        rows = test.select("tbody tr")
        rows.remove(rows[5])
        for row in rows:
            name = row.select("th")[0].get_text().encode('utf-8')
            line = [datetime.datetime.strptime(date, "%Y-%m-%d").date(), team.name , opponent, location, name]
            data = row.select('td')
            for x in data:
                if not '_pct' in x['data-stat']:
                    line.append(x.get_text().encode("utf-8"))
            coolness = getCoolness(line)
            line.append(coolness)
            series = pd.Series(line,colHeads)
            df = df.append([series], ignore_index=True)
        team.box = df
        #df.to_csv("csv/" + date + "-" + team.name + ".csv")
    return game
    
def getCoolness(line):
    mins = float(line[5])
    fg_made = float(line[6])
    fg_attempt = float(line[7])
    two_made = float(line[8])
    two_attempt = float(line[9])
    three_made = float(line[10])
    three_attempt = float(line[11])
    ft_made = float(line[12])
    ft_attempt = float(line[13])
    orb = float(line[14])
    drb = float(line[15])
    trb = float(line[16])
    ast = float(line[17])
    stl = float(line[18])
    blk = float(line[19])
    tov = float(line[20])
    pf = float(line[21])
    pts = float(line[22])
    
    coolness = 0
    
    if pts >= 10:
        coolness += 1
    if pts >= 20:
        coolness += 1
    if pts >= 25:
        coolness += 1
    if pts >= 30:
        coolness += 1
    if pts >= 35:
        coolness += 1
    if pts >= 40:
        coolness += 1
    if trb >= 8:
        coolness += 1
    if trb >= 10:
        coolness += 1
    if trb >= 12:
        coolness += 1
    if trb >= 15:
        coolness += 1
    if orb >= 5:
        coolness += 1
    if ast >= 8:
        coolness += 1
    if ast >= 10:
        coolness += 1
    if ast >= 12:
        coolness += 1
    if ast >= 15:
        coolness += 1
    if blk >= 2:
        coolness += 1
    if blk >= 3:
        coolness += 1
    if blk >= 4:
        coolness += 1
    if blk >= 5:
        coolness += 1
    if stl >= 3:
        coolness += 1
    if stl >= 5:
        coolness += 1
    if ft_attempt > 0:
        if ft_attempt == ft_made and ft_attempt >= 5:
            coolness += 1
        if ft_made/ft_attempt >= .8 and ft_attempt >= 8:
            coolness += 1
    if fg_attempt > 0:
        if fg_attempt >= 10 and fg_made/fg_attempt >= .5:
            coolness += 1
        if fg_attempt >= 10 and fg_made/fg_attempt >= .75:
            coolness += 1
        if fg_attempt >= 10 and fg_made/fg_attempt >= .80:
            coolness += 1
        if fg_attempt >= 10 and fg_made/fg_attempt >= .90:
            coolness += 1
        if fg_attempt >= 10 and fg_made == fg_attempt:
            coolness += 1
        if three_attempt > 0:
            if three_attempt >= 5 and three_made/three_attempt >= .5:
                coolness += 1
            if three_attempt >= 5 and three_made == three_attempt:
                coolness += 1
        
    return coolness
    
    
def processGame(game, date):
    print "Processing " + game.away.name + " vs. " + game.home.name
    page = requests.get(game.link)
    html = BeautifulSoup(page.content, 'html.parser')
    return getBox(html, game, date)
    
def insertToDb(game):
    print "Inserting " + game.away.name + " vs. " + game.home.name
    homeLines = []
    awayLines = []
    try:
        homeLines = game.home.box.values.tolist()
    except:
        log.write("ERROR: " + game.home.name + " doesn't have box score" + '\n')
    try:
        awayLines = game.away.box.values.tolist()
    except:
        log.write("ERROR: " + game.away.name + " doesn't have box score" + '\n')
    
    lines = homeLines + awayLines
    
    for line in lines:
        insertGameLine(line)
        
def incrementDate(date):
    year, month, day = date.split('-')
    endDay = {
        '01':'31',
        '02':'28',
        '03':'31',
        '04':'30',
        '05':'31',
        '06':'30',
        '07':'31',
        '08':'31',
        '09':'30',
        '10':'31',
        '11':'30',
        '12':'31'
    }
    if int(year) % 4 == 0:
        endDay['2'] = '29'
    day = str(int(day) + 1)
    if int(day) > int(endDay[month]):
        day = '01'
        if month == '12':
            month = '01'
            year = str(int(year) + 1)
        else:
            month = str(int(month) + 1)
    if len(day) == 1:
        day = '0' + day
    if len(month) == 1:
        month = '0' + month
    return year + '-' + month + '-' + day

def main():
    args = parseArgs()
    start = args.start
    end = args.end
    currYear, currMonth, currDay = start.split('-')
    endYear, endMonth, endDay = end.split('-')
    date = start
    while int(currYear) <= int(endYear) and int(currMonth) <= int(endMonth) and int(currDay) <= int(endDay):
        games = getGames(date)
        games = [games[0]]
        for game in games:
            game = processGame(game, date)
        for game in games:
            insertToDb(game)
        date = incrementDate(date)
        currYear, currMonth, currDay = date.split('-')
    log.close()
        
if __name__ == "__main__": main()    