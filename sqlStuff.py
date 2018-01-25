import sqlite3 as sql
import pandas as pd
import string

db = "cbb_17_18.db"

def getTeamId(teamName):
    conn = sql.connect(db)
    c = conn.cursor()
    
    var = (teamName,)
    
    c.execute("SELECT id FROM team WHERE name = ?", var)
    
    temp = c.fetchone()
    
    if temp == None:
        c.execute("INSERT INTO team (name) VALUES (?)", var)
        c.execute("SELECT id FROM team WHERE name = ?", var)
        temp = c.fetchone()
        conn.commit()
    
    conn.close()
    return temp[0]
    
def getPlayerId(playerName, team = None):
    conn = sql.connect(db)
    c = conn.cursor()
        
    if team == None:
        var = (playerName,)
        c.execute("SELECT team.name FROM player INNER JOIN team ON player.team_id = team.id WHERE player.name = ? ", var)
        temp = c.fetchall()
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
            team = temp[0]
        else:
            print "No Player with that name"
            return
        
    teamId = getTeamId(team)
    var = (playerName, teamId)
    c.execute("SELECT id FROM player WHERE name = ? AND team_id = ?", var)
    temp = c.fetchone()
        
    if temp == None:
        c.execute("INSERT INTO player (name, team_id) VALUES (?,?)", var)
        conn.commit()
        c.execute("SELECT id FROM player WHERE name = ? AND team_id = ?", var)
        temp = c.fetchone()    
    
    conn.close()
    return temp[0]

def insertGameLine(line):
    conn = sql.connect(db)
    c = conn.cursor()
    
    date, team, opponent, location, player, mins, fg_made, fg_attempt, two_made, two_attempt, three_made, three_attempt, ft_made, ft_attempt, orb, drb, trb, ast, stl, blk, tov, pf, pts, coolness = line
    
    teamId = getTeamId(team)
    opponentId = getTeamId(opponent)
    playerId = getPlayerId(player, teamId)
    
    var = (date, playerId, teamId, opponentId, location, mins, fg_made, fg_attempt, two_made, two_attempt, three_made, three_attempt, ft_made, ft_attempt, orb, drb, trb, ast, stl, blk, tov, pf, pts, coolness)
    
    c.execute("INSERT INTO game_line (date, player_id, team_id, opponent_id, location, minutes, fg_made, fg_attempt, two_made, two_attempt, three_made, three_attempt, ft_made, ft_attempt, orb, drb, trb, ast, stl, blk, tov, pf, pts, coolness) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", var)
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
        "INNER JOIN player ON player.id = game_line.player_id WHERE player.id = ?;",
        
    ]
    
    query = ""
    
    for x in queryList: query += x
    
    c.execute(query, var)
    temp = c.fetchone()
    
    colNames = ['Player', 'School', 'Games', 'MPG', 'PPG', 'APG', 'ORPG', 'DRPG', 'RPG', 'SPG', 'BPG', 'TPG', 'CPG', 'FG%', '2P%', '3P%', 'FT%', 'Points', 'Asists', 'ORB', 'DRB', 'TRB', 'Coolness']
    
    conn.close()
    
    return pd.Series(temp, colNames)#.round(2)
    
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
        "INNER JOIN player ON player.id = game_line.player_id  WHERE player.id = ?;"
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