#import psycopg2 as sql
import sqlite3 as sql
import pandas as pd
import string
from Objects import Game
from getConference import getConfs

#db = "dbname='Test' user='postgres' host='localhost' password=''"
db = "cbb_17_18.db"

def getTeamId(teamName):
    conn = sql.connect(db)
    c = conn.cursor()

    var = (teamName,)
    
    c.execute("SELECT id FROM team WHERE name = ?", var)
    
    temp = c.fetchone()
    
    if temp == None:
        c.execute("INSERT INTO team (name, conference) VALUES (?,'none')", var)
        c.execute("SELECT id FROM team WHERE name = ?", var)
        temp = c.fetchone()
        conn.commit()
    
    conn.close()
    return temp[0]

def getTeamConf(teamId):
    conn = sql.connect(db)
    c = conn.cursor()

    var = (teamId,)
    
    c.execute("SELECT conference FROM team WHERE id = ?", var)
    temp = c.fetchone()
    conn.commit()

    return temp[0]
    
def getPlayerId(playerName, team = None):
    conn = sql.connect(db)
    c = conn.cursor()
        
    if team == None:
        var = (playerName,)
        c.execute("SELECT team.name FROM player INNER JOIN team ON player.team_id = team.id WHERE player.name = ? COLLATE NOCASE", var)
        temp = c.fetchall()
        print temp
        if len(temp) > 1:
            print "There are multiple players with the name {} which one would you like".format(playerName)
            teams = [x[0] for x in temp]
            for y in teams:
                print "- {}".format(y)
            team = raw_input()
            team = team.lower()
            team = team.replace(' ', '-')
            while team not in teams:
                print "Please enter a valid team name"
                team = raw_input()
                team = team.lower()
                team = team.replace(' ', '-')
        elif len(temp) == 1:
            team = temp[0][0]
        else:
            print "No Player with that name"
            return
        
    teamId = getTeamId(team)
    var = (playerName, teamId)
    c.execute("SELECT id FROM player WHERE name = ? AND team_id = ? COLLATE NOCASE", var)
    temp = c.fetchone()
        
    if temp == None:
        c.execute("INSERT INTO player (name, team_id) VALUES (?,?)", var)
        conn.commit()
        c.execute("SELECT id FROM player WHERE name = ? AND team_id = ? COLLATE NOCASE", var)
        temp = c.fetchone()    
    
    conn.close()
    return temp[0]

def insertGameLine(line, gameId):
    conn = sql.connect(db)
    c = conn.cursor()
    
    date, team, opponent, location, player, mins, fg_made, fg_attempt, two_made, two_attempt, three_made, three_attempt, ft_made, ft_attempt, orb, drb, trb, ast, stl, blk, tov, pf, pts, coolness = line
    
    teamId = getTeamId(team)
    opponentId = getTeamId(opponent)
    playerId = getPlayerId(player, team)
    
    var = (gameId, date, playerId, teamId, opponentId, location, mins, fg_made, fg_attempt, two_made, two_attempt, three_made, three_attempt, ft_made, ft_attempt, orb, drb, trb, ast, stl, blk, tov, pf, pts, coolness)
    
    c.execute("INSERT INTO game_line (game_id, date, player_id, team_id, opponent_id, location, minutes, fg_made, fg_attempt, two_made, two_attempt, three_made, three_attempt, ft_made, ft_attempt, orb, drb, trb, ast, stl, blk, tov, pf, pts, coolness) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", var)
    conn.commit()
    conn.close()

def insertGame(game):
    conn = sql.connect(db)
    c = conn.cursor()

    isConf = 0
    date = game.date

    homeId = getTeamId(game.home.name)
    homeScore = game.homeScore
    homeConf = getTeamConf(homeId)

    awayId = getTeamId(game.away.name)
    awayScore = game.awayScore
    awayConf = getTeamConf(awayId)

    if homeConf == awayConf: isConf = 1

    var = (isConf, date, homeId, awayId, homeScore, awayScore)

    c.execute("INSERT INTO game (conf_game, date, home_id, away_id, home_score, away_score) VALUES (?,?,?,?,?,?)", var)
    conn.commit()

    var = (date, homeId, awayId)

    c.execute("SELECT id FROM game WHERE date = ? AND home_id = ? AND away_id = ?", var)
    temp = c.fetchone()

    conn.close()

    if homeScore > awayScore:
        updateWinner(homeId, isConf)
        updateLoser(awayId, isConf)
    else:
        updateWinner(awayId, isConf)
        updateLoser(homeId, isConf)

    return temp[0]

def updateWinner(teamId, isConf):
    conn = sql.connect(db)
    c = conn.cursor()

    var = (teamId,)

    c.execute("UPDATE team SET wins = wins + 1 WHERE id = ?", var)

    if isConf:
        c.execute("UPDATE team SET conf_wins = conf_wins + 1 WHERE id = ?", var)
    conn.commit()
    conn.close()

def updateLoser(teamId, isConf):
    conn = sql.connect(db)
    c = conn.cursor()

    var = (teamId,)

    c.execute("UPDATE team SET losses = losses + 1 WHERE id = ?", var)

    if isConf:
        c.execute("UPDATE team SET conf_losses = conf_losses + 1 WHERE id = ?", var)
    conn.commit()
    conn.close()

def insertConfs():
    conn = sql.connect(db)
    c = conn.cursor()
    c.execute("INSERT INTO conference (abbrv, name) VALUES ('none','Non-Divison 1 Teams')")
    confDict, confAbbrv = getConfs()
    confs = confDict.keys()
    for conf in confs:
        confVar = (confAbbrv[conf], conf)
        c.execute("INSERT INTO conference (abbrv, name) VALUES (?,?)", confVar)
        teamList = confDict[conf]
        for team in teamList:
            teamVar = (confAbbrv[conf], team)
            c.execute("INSERT INTO team (conference, name, wins, losses, conf_wins, conf_losses) VALUES (?,?,0,0,0,0)", teamVar)
    
    conn.commit()        
    conn.close()
    
def getPlayerLine(playerName):
    conn = sql.connect(db)
    c = conn.cursor()

    playerName = string.capwords(playerName)
    
    playerId = getPlayerId(playerName)
    
    var = (playerId,)
    
    queryList = [
        "SELECT player.name as Player, ",
        "team.name as School, "
        "CAST(Count(*) as float) as Games, ",
        "SUM(minutes) / CAST(Count(*) as float) as MPG, ",
        "SUM(pts) / CAST(Count(*) as float) as PPG, ",
        "SUM(ast) / CAST(Count(*) as float) as APG, ",
        "SUM(orb) / CAST(Count(*) as float) as ORPG, ",
        "SUM(drb) / CAST(Count(*) as float) as DRPG, ",
        "SUM(trb) / CAST(Count(*) as float) as RPG, ",
        "SUM(stl) / CAST(Count(*) as float) as SPG, ",
        "SUM(blk) / CAST(Count(*) as float) as BPG, ",
        "SUM(tov) / CAST(Count(*) as float) as TPG, ",
        "SUM(coolness) / CAST(Count(*) as float) as CPG, ",
        "SUM(fg_made) / CAST(SUM(fg_attempt) as float) as 'FG%', ",
        "SUM(two_made) / CAST(SUM(two_attempt) as float) as '2P%', ",
        "SUM(three_made) / CAST(SUM(three_attempt) as float) as '3P%', ",
        "SUM(ft_made) / CAST(SUM(ft_attempt) as float) as 'FT%', ",
        "SUM(pts) as Points, ",
        "SUM(ast) as Asists, ",
        "SUM(orb) as ORB, ",
        "SUM(drb) as DRB, ",
        "SUM(trb) as TRB, ",
        "SUM(coolness) as Coolness ",
        "FROM game_line ",
        "INNER JOIN team ON team.id = game_line.team_id ",
        "INNER JOIN player ON player.id = game_line.player_id WHERE player.id = ? "
    ]
    
    query = ""
    
    for x in queryList: query += x
    
    c.execute(query, var)
    temp = c.fetchone()
    
    colNames = ['Player', 'School', 'Games', 'MPG', 'PPG', 'APG', 'ORPG', 'DRPG', 'RPG', 'SPG', 'BPG', 'TPG', 'CPG', 'FG%', '2P%', '3P%', 'FT%', 'Points', 'Asists', 'ORB', 'DRB', 'TRB', 'Coolness']
    
    conn.close()
    
    return pd.Series(temp, colNames)#.round(2)

def getAllPlayerLines():
    conn = sql.connect(db)
    c = conn.cursor()
    
    queryList = [
        "SELECT player.name as Player, ",
        "team.name as School, "
        "CAST(Count(*) as float) as Games, ",
        "SUM(minutes) / CAST(Count(*) as float) as MPG, ",
        "SUM(pts) / CAST(Count(*) as float) as PPG, ",
        "SUM(ast) / CAST(Count(*) as float) as APG, ",
        "SUM(orb) / CAST(Count(*) as float) as ORPG, ",
        "SUM(drb) / CAST(Count(*) as float) as DRPG, ",
        "SUM(trb) / CAST(Count(*) as float) as RPG, ",
        "SUM(stl) / CAST(Count(*) as float) as SPG, ",
        "SUM(blk) / CAST(Count(*) as float) as BPG, ",
        "SUM(tov) / CAST(Count(*) as float) as TPG, ",
        "SUM(coolness) / CAST(Count(*) as float) as CPG, ",
        "SUM(fg_made) / CAST(SUM(fg_attempt) as float) as 'FG%', ",
        "SUM(two_made) / CAST(SUM(two_attempt) as float) as '2P%', ",
        "SUM(three_made) / CAST(SUM(three_attempt) as float) as '3P%', ",
        "SUM(ft_made) / CAST(SUM(ft_attempt) as float) as 'FT%', ",
        "SUM(pts) as Points, ",
        "SUM(ast) as Asists, ",
        "SUM(orb) as ORB, ",
        "SUM(drb) as DRB, ",
        "SUM(trb) as TRB, ",
        "SUM(coolness) as Coolness ",
        "FROM game_line ",
        "INNER JOIN player ON player.id = game_line.player_id ",
        "INNER JOIN team ON team.id = game_line.team_id ",
        "GROUP BY player_id;"
    ]
    
    query = ""
    
    for x in queryList: query += x
    
    c.execute(query)
    temp = c.fetchall()
    
    colNames = ['Player', 'School', 'Games', 'MPG', 'PPG', 'APG', 'ORPG', 'DRPG', 'RPG', 'SPG', 'BPG', 'TPG', 'CPG', 'FG%', '2P%', '3P%', 'FT%', 'Points', 'Asists', 'ORB', 'DRB', 'TRB', 'Coolness']
    df = pd.DataFrame(temp)
    df.columns = colNames
    conn.close()
    return df
    #return pd.DataFrame(temp, colNames)#.round(2)
    
def getSimplePlayerLine(playerName):
    conn = sql.connect(db)
    c = conn.cursor()
    
    playerName = string.capwords(playerName)
    
    playerId = getPlayerId(playerName)

    var = (playerId,)
    
    queryList = [
        "SELECT player.name as Player, ",
        "team.name as School, ",
        "CAST(Count(*) as float) as Games, ",
        "SUM(minutes) / CAST(Count(*) as float) as MPG, ",
        "SUM(pts) / CAST(Count(*) as float) as PPG, ",
        "SUM(ast) / CAST(Count(*) as float) as APG, ",
        "SUM(trb) / CAST(Count(*) as float) as RPG, ",
        "SUM(stl) / CAST(Count(*) as float) as SPG, ",
        "SUM(blk) / CAST(Count(*) as float) as BPG, ",
        "SUM(tov) / CAST(Count(*) as float) as TPG, ",
        "SUM(fg_made) / CAST(SUM(fg_attempt) as float) as 'FG%', ",
        "SUM(two_made) / CAST(SUM(two_attempt) as float) as '2P%', ",
        "SUM(three_made) / CAST(SUM(three_attempt) as float) as '3P%', ",
        "SUM(ft_made) / CAST(SUM(ft_attempt) as float) as 'FT%' ",
        "FROM game_line ",
        "INNER JOIN team ON team.id = player.team_id ",
        "INNER JOIN player ON player.id = game_line.player_id  WHERE player.id = ? ",
        "COLLATE NOCASE;"
    ]
    
    query = ""
    
    for x in queryList: query += x
    
    c.execute(query, var)
    temp = c.fetchone()
    
    colNames = ['Player', 'School', 'Games', 'MPG', 'PPG', 'APG', 'RPG', 'SPG', 'BPG', 'TPG', 'FG%', '2P%', '3P%', 'FT%']
    
    conn.close()
    
    return pd.Series(temp, colNames)
    
    
def getTeamPage(teamName):
    conn = sql.connect(db)
    c = conn.cursor()
    
    teamName = teamName.lower()
    teamName = teamName.replace(' ', '-')
    
    colNames = ['Player', 'Games', 'MPG', 'PPG', 'APG', 'RPG', 'SPG', 'BPG', 'TPG', 'FG%', '2P%', '3P%', 'FT%']
    
    var = (teamName, )
    
    queryList = [
        "SELECT player.name as Player, ",
        "CAST(Count(*) as float) as Games, ",
        "SUM(minutes) / CAST(Count(*) as float) as MPG, ",
        "SUM(pts) / CAST(Count(*) as float) as PPG, ",
        "SUM(ast) / CAST(Count(*) as float) as APG, ",
        "SUM(trb) / CAST(Count(*) as float) as RPG, ",
        "SUM(stl) / CAST(Count(*) as float) as SPG, ",
        "SUM(blk) / CAST(Count(*) as float) as BPG, ",
        "SUM(tov) / CAST(Count(*) as float) as TPG, ",
        "SUM(fg_made) / CAST(SUM(fg_attempt) as float) as 'FG%', ",
        "SUM(two_made) / CAST(SUM(two_attempt) as float) as '2P%', ",
        "SUM(three_made) / CAST(SUM(three_attempt) as float) as '3P%', ",
        "SUM(ft_made) / CAST(SUM(ft_attempt) as float) as 'FT%' ",
        "FROM game_line ",
        "INNER JOIN team ON team.id = player.team_id ",
        "INNER JOIN player ON player.id = game_line.player_id WHERE team.name = ? "
        "GROUP BY player_id;"
    ]
    
    query = ""
    
    for x in queryList: query += x
    
    c.execute(query , var)

    temp = c.fetchall()
    
    page = pd.DataFrame(temp, columns = colNames)
     
    conn.close()    
        
    return page.round(2)

def getLeaderboard(stat, limit):
    conn = sql.connect(db)
    c = conn.cursor()
    
    statQuery = {
        "Coolness" : "SUM(coolness)",
        "Points" : "SUM(pts)",
        "Asists" : "SUM(ast)",
        "Rebounds" : "SUM(trb)",
        "Offensive Rebounds" : "SUM(orb)",
        "Defensive Rebounds" : "SUM(drb)",
        "Steals" : "SUM(stl)",
        "CPG" : "SUM(coolness)/Cast(COUNT(*) as float)",
        "PPG" : "SUM(pts)/Cast(COUNT(*) as float)",
        "APG" : "SUM(ast)/Cast(COUNT(*) as float)",
        "RPG" : "SUM(trb)/Cast(COUNT(*) as float)",
        "ORPG" : "SUM(orb)/Cast(COUNT(*) as float)",
        "DRPG" : "SUM(drb)/Cast(COUNT(*) as float)",
        "SPG" : "SUM(stl)/Cast(COUNT(*) as float)"
    }
        
    var = (limit, )
    
    query = ""
    
    queryList = [
        "SELECT player.name as Player, ",
        "team.name as Team, "
        "CASE WHEN CAST(Count(*) as float) >= 10 THEN {} END as stat ".format(statQuery[stat]),
        "FROM game_line ",
        "INNER JOIN player ON player.id = game_line.player_id ",
        "INNER JOIN team ON team.id = game_line.team_id ",
        "GROUP BY player_id ",
        "ORDER by stat DESC ",
        "LIMIT ?;"
    ]
        
    for x in queryList: query += x
    
    c.execute(query, var)
    
    result = c.fetchall()
    
    players = [x[0] for x in result]
    teams = [string.capwords(x[1].replace('-',' ')) for x in result]
    stats = [x[2] for x in result]
    
    df = pd.DataFrame(
        {
            'Player': players,
            'Team': teams,
            stat: stats
        }
    )
    
    df = df[[u'Player', u'Team', stat]]
    
    df.index = df.index + 1
    
    conn.close()
    
    return df.round(2)
    
def getWatchability():
    conn = sql.connect(db)
    c = conn.cursor()
    c.execute("SELECT team.name, team_id, SUM(minutes), SUM(coolness) FROM game_line INNER JOIN team on team_id = team.id GROUP BY team_id")
    temp = c.fetchall()
    
    df = pd.DataFrame(temp, columns=["team", "id", "minutes", "coolness"])
    
    watch = []
    for index, row in df.iterrows():
        watch.append(float(row.coolness)/row.minutes)
    
    normed = [0.0] * len(watch)
    mean = sum(watch)/len(watch)
    
    for i in range(len(watch)):
        inc = watch[i] - mean
        normed[i] = inc/mean * 100
        
    watchFrame = pd.DataFrame({'Team':df.team.values, 'Watchability':normed})
    watchFrame = watchFrame.sort_values(by='Watchability', ascending=False)
    
    conn.close()
    return watchFrame

def getMaxDate():
    conn = sql.connect(db)
    c = conn.cursor()
    c.execute("SELECT max(date) FROM game_line;")
    date = c.fetchone()[0]
    if date == None: return "The database is empty"
    else: return date.encode("utf-8")