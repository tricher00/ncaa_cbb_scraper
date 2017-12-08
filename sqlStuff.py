import sqlite3 as sql
import pandas as pd

db = "cbb_17_18.db"

def getTeamId(teamName):
    conn = sql.connect(db)
    c = conn.cursor()
    
    teamName = teamName.lower()
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
    
def getPlayerId(playerName, teamId):
    conn = sql.connect(db)
    c = conn.cursor()
    
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
    
    var = (playerName,)
    
    c.execute("SELECT player.name as Player, CAST(Count(*) as float) as Games, SUM(minutes) / CAST(Count(*) as float) as MPG, SUM(pts) / CAST(Count(*) as float) as PPG, SUM(ast) / CAST(Count(*) as float) as APG, SUM(orb) / CAST(Count(*) as float) as ORPG, SUM(drb) / CAST(Count(*) as float) as DRPG, SUM(trb) / CAST(Count(*) as float) as RPG, SUM(stl) / CAST(Count(*) as float) as SPG, SUM(blk) / CAST(Count(*) as float) as BPG, SUM(tov) / CAST(Count(*) as float) as TPG, SUM(coolness) / CAST(Count(*) as float) as CPG, SUM(fg_made) / CAST(SUM(fg_attempt) as float) as 'FG%', SUM(two_made) / CAST(SUM(two_attempt) as float) as '2P%', SUM(three_made) / CAST(SUM(three_attempt) as float) as '3P%', SUM(ft_made) / CAST(SUM(ft_attempt) as float) as 'FT%', SUM(pts) as Points, SUM(ast) as Asists, SUM(orb) as ORB, SUM(drb) as DRB, SUM(trb) as TRB, SUM(coolness) as Coolness FROM game_line  INNER JOIN player  ON player.id = game_line.player_id  WHERE player.name = ?;", var)
    temp = c.fetchone()
    
    colNames = ['Player', 'Games', 'MPG', 'PPG', 'APG', 'ORPG', 'DRPG', 'RPG', 'SPG', 'BPG', 'TPG', 'CPG', 'FG%', '2P%', '3P%', 'FT%', 'Points', 'Asists', 'ORB', 'DRB', 'TRB', 'Coolness']
    
    return pd.Series(temp, colNames)
    
def getTeamPage(teamName):
    conn = sql.connect(db)
    c = conn.cursor()

    var = (teamName, )

    c.execute("SELECT player.name FROM player INNER JOIN team ON team.id = player.team_id WHERE team.name = ?" , var)

    temp = c.fetchall()

    players = [x[0].encode("utf-8") for x in temp]
    #TODO: Get player line for all players

    