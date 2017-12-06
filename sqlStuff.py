import sqlite3 as sql

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