import pandas as pd
import string
from boxscoreParse import getGames, processGame, insertToDb
from getSchedule import getGames as getSched
from Objects import *
from sqlStuff import *

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
    
def print_full(x):
    pd.set_option('display.max_rows', len(x))
    print(x)
    pd.reset_option('display.max_rows')

def isDateLessThan(date, compare):
    year, month, day = [int(x) for x in date.split('-')]
    comYear, comMonth, comDay = [int(x) for x in compare.split('-')]

    if year < comYear: return True
    elif month < comMonth: return True
    elif day <= comDay: return True
    else: return False

def updateDb():
    print "The database has been updated through {}".format(getMaxDate())
    sm = raw_input("Would you like to insert games for a (s)ingle day or (m)ultiple days? (s/m): ")
    
    if sm == 'm':
        start = raw_input("Start Date (YYYY-MM-DD): ")
        end = raw_input("End Date (YYYY-MM-DD): ")
        
        currYear, currMonth, currDay = start.split('-')
        endYear, endMonth, endDay = end.split('-')
        date = start
        isLessThan = isDateLessThan(start, end)
        while isLessThan:
            print date
            games = getGames(date)
            for game in games:
                game = processGame(game, date)
            for game in games:
                insertToDb(game)
            date = incrementDate(date)
            isLessThan = isDateLessThan(date, end)
            currYear, currMonth, currDay = date.split('-')
    elif sm == 's':
        date = raw_input("Date (YYYY-MM-DD): ")
        games = getGames(date)
        for game in games:
            game = processGame(game, date)
        for game in games:
            insertToDb(game)
            
    else: 
        print "Please enter a valid input"
        
def schedule():
    date = raw_input("What date would you like to get the schedule for? (YYYY-MM-DD): ")
    games = getSched(date)
    watch = getWatchability()
    df = pd.DataFrame(columns=["Away", "Home", "Watchability"])
    
    for game in games:
        away = string.capwords(game.away.name.replace('-',' '))
        home = string.capwords(game.home.name.replace('-',' '))
        if game.away.name in watch.Team.values:
            awayWatch = float(watch[watch.Team == game.away.name].Watchability)
        else: 
            awayWatch = 0
        if game.home.name in watch.Team.values:
            homeWatch = float(watch[watch.Team == game.home.name].Watchability)
        else:
            homeWatch = 0
        x = (awayWatch + homeWatch)/2
        df = df.append({"Away":away, "Home":home, "Watchability":x}, ignore_index=True)
    
    df = df.sort_values(by="Watchability", ascending=False).reset_index(drop=True).round()
    ints = [int(x) for x in df.Watchability.values]
    df.Watchability = ints
    print_full(df)
    
def getPlayer():
    player = raw_input("Player Name: ")
    lineType = raw_input("Would you like the (f)ull line or the (s)imple line? (f/s): ")
    
    lineType = lineType.lower()
    
    if lineType == 's':
        print getSimplePlayerLine(player)
    elif lineType == 'f':
        print getPlayerLine(player)
    else:
        print "Please enter a valid input"
        
def getTeam():
    team = raw_input("Team Name: ")
    print getTeamPage(team)
    
def leaderboard():
    stat = raw_input("Please enter a stat: ")
    limit = raw_input("How many players would you like to see?: ")
    print getLeaderboard(stat, limit)

def getAllStats():
    df = getAllPlayerLines()
    date = getMaxDate()
    df.to_csv("full_stats_{}.csv".format(date))

def getMatchup():
    team1 = raw_input("Enter the first team name: ")
    team2 = raw_input("Enter the second team name: ")

    team1Dict = getMatchupInfo(team1)
    team2Dict = getMatchupInfo(team2)

    data = []
    data.append([string.capwords(team1), "School Name", string.capwords(team2)])
    data.append(["{}: {}".format(team1Dict['top1'][0], team1Dict['top1'][1]), "Top Player 1", "{}: {}".format(team2Dict['top1'][0], team2Dict['top1'][1])])
    data.append(["{}: {}".format(team1Dict['top2'][0], team1Dict['top2'][1]), "Top Player 2", "{}: {}".format(team2Dict['top2'][0], team2Dict['top2'][1])])
    data.append(["{}: {}".format(team1Dict['top3'][0], team1Dict['top3'][1]), "Top Player 3", "{}: {}".format(team2Dict['top3'][0], team2Dict['top3'][1])])
    data.append(["{}: {}".format(team1Dict['topPpg'][0], team1Dict['topPpg'][1]), "Top Scorer", "{}: {}".format(team2Dict['topPpg'][0], team2Dict['topPpg'][1])])
    data.append(["{}: {}".format(team1Dict['topReb'][0], team1Dict['topReb'][1]), "Top Rebounder", "{}: {}".format(team2Dict['topReb'][0], team2Dict['topReb'][1])])
    data.append([format(team1Dict['fgPer'], '.3f'), "FG%", format(team2Dict['fgPer'], '.3f')])
    data.append([format(team1Dict['twoPer'], '.3f'), "2P%", format(team2Dict['twoPer'], '.3f')])
    data.append([format(team1Dict['threePer'], '.3f'), "3P%", format(team2Dict['threePer'], '.3f')])
    data.append([format(team1Dict['ftPer'], '.3f'), "FT%", format(team2Dict['ftPer'], '.3f')])

    df = pd.DataFrame(data)
    print(df.to_string(header=False, index=False, col_space=20))
    
def getMatchupInfo(team):
    teamPage = getTeamPage(team)

    teamDict = {}
    topPlayers = teamPage.sort_values(by=['CPG'], ascending = False).head(3).reset_index()
    
    teamDict['top1'] = (topPlayers.iloc[0]['Player'], topPlayers.iloc[0]['CPG'])
    teamDict['top2'] = (topPlayers.iloc[1]['Player'], topPlayers.iloc[1]['CPG'])
    teamDict['top3'] = (topPlayers.iloc[2]['Player'], topPlayers.iloc[2]['CPG'])

    topPpg = teamPage.sort_values(by=['PPG'], ascending = False).head(1).reset_index()
    teamDict['topPpg'] = (topPpg.iloc[0]['Player'], topPpg.iloc[0]['PPG'])

    topReb = teamPage.sort_values(by=['RPG'], ascending = False).head(1).reset_index()
    teamDict['topReb'] = (topReb['Player'].iloc[0], topReb['RPG'].iloc[0])

    fga = float(teamPage['FGA'].values.sum())
    fgm = float(teamPage['FGM'].values.sum())
    twopa = float(teamPage['2PA'].values.sum())
    twopm = float(teamPage['2PM'].values.sum())
    threepa = float(teamPage['3PA'].values.sum())
    threepm = float(teamPage['3PM'].values.sum())
    fta = float(teamPage['FTA'].values.sum())
    ftm = float(teamPage['FTM'].values.sum())

    teamDict['fgPer'] = fgm/fga
    teamDict['twoPer'] = twopm/twopa
    teamDict['threePer'] = threepm/threepa
    teamDict['ftPer'] = ftm/fta

    return teamDict

def main():
    print "What would like to do?"
    print "U: Update Database"
    print "S: Get Schedule"
    print "P: Get Player Line"
    print "T: Get Team Page"
    print "L: Get Leaderboard"
    print "M: Get Matchup"
    print "C: Get CSV of all stats"
    
    var = raw_input()
    
    var = var.upper()
    
    if var == 'U' : updateDb()
    elif var == 'S' : schedule()
    elif var == 'P' : getPlayer()
    elif var == 'T' : getTeam()
    elif var == 'L' : leaderboard()
    elif var == 'M' : getMatchup()
    elif var == 'C' : getAllStats()
    else: print "Please enter a valid input"
            
if __name__ == "__main__": main()    
    