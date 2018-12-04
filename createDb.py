import sqlite3 as sql
from sqlStuff import insertConfs

def main():
    db = "cbb_18_19.db"

    conn = sql.connect(db)
    c = conn.cursor()

    c.execute(
        "CREATE TABLE game_line(id INTEGER PRIMARY KEY AUTOINCREMENT, game_id INTEGER, date DATE, player_id VARCHAR, team_id INTEGER, opponent_id INTEGER, location VARCHAR, minutes INTEGER, fg_made INTEGER, fg_attempt INTEGER, two_made INTEGER, two_attempt INTEGER, three_made INTEGER, three_attempt INTEGER, ft_made INTEGER, ft_attempt INTEGER, orb INTEGER, drb INTEGER, trb INTEGER, ast INTEGER, stl INTEGER, blk INTEGER, tov INTEGER, pf INTEGER, pts INTEGER, coolness INTEGER);"
    )
    print("Created game_line table")
    c.execute(
        "CREATE TABLE team(id INTEGER PRIMARY KEY AUTOINCREMENT, conference VARCHAR, name VARCHAR, wins INTEGER, losses INTEGER, conf_wins INTEGER, conf_losses INTEGER);"
    )
    print("Created team table")
    c.execute(
        "CREATE TABLE conference(abbrv VARCHAR PRIMARY KEY, name VARCHAR);"
    )
    print("Created conference table")
    c.execute(
        "CREATE TABLE player(id VARCHAR PRIMARY KEY, name VARCHAR, team_id INTEGER);"
    )
    print("Created player table")
    c.execute(
        "CREATE TABLE game(id INTEGER PRIMARY KEY AUTOINCREMENT, date DATE, conf_game INTEGER, home_id INTEGER, away_id INTEGER, home_score INTEGER, away_score INTEGER);"
    )
    print("Created game table")
    insertConfs()

if __name__ == "__main__": main()
