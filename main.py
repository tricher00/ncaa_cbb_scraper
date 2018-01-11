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

def updateDb():
    sm = raw_input("Would you like to insert games for a (s)ingle day or (m)ultiple days? (s/m): ")
    
    if sm == 'm':
        start = raw_input("Start Date (YYYY-MM-DD): ")
        end = raw_input("End Date (YYYY-MM-DD): ")
        
        currYear, currMonth, currDay = start.split('-')
        endYear, endMonth, endDay = end.split('-')
        date = start
        while int(currYear) <= int(endYear) and int(currMonth) <= int(endMonth) and int(currDay) <= int(endDay):
            games = getGames(date)
            for game in games:
                game = processGame(game, date)
            for game in games:
                insertToDb(game)
            date = incrementDate(date)
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
    for game in games:
        print "Away: " + game.away.name
        print "Home: " + game.home.name
        print
    
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

def main():
    log = open("log.txt", "w")
    print "What would like to do?"
    print "U: Update Database"
    print "S: Get Schedule"
    print "P: Get Player Line"
    print "T: Get Team Page"
    
    var = raw_input()
    
    var = var.upper()
    
    if var == 'U' : updateDb()
    elif var == 'S' : schedule()
    elif var == 'P' : getPlayer()
    elif var == 'T' : getTeam()
    else: print "Please enter a valid input"
    
    log.close()
        
if __name__ == "__main__": main()    
    