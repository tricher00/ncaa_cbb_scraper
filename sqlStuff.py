import sqlite3 as sql

db = "testDB.db"

def getTeamId(teamName):
    conn = sql.connect(db)
    c = conn.cursor()
    
    c.execute("SELECT id FROM team WHERE name = ?", (team,))
    
    temp = c.fetchone()
    
    if temp == None:
        c.execute("INSERT INTO team (name) VALUES (?)", (team,))
        c.execute("SELECT id FROM team WHERE name = ?", (team,))
    
    return temp[0]