import sqlite3 as sql
from getConference import getConfs

def main():
    db = "cbb_17_18.db"
    conn = sql.connect(db)
    c = conn.cursor()

    confDict, confAbbrv = getConfs()

    confs = confDict.keys()
    i = 0

    for conf in confs:
        confVar = (i, conf)
        c.execute("UPDATE conference SET abbrv = ? WHERE name = ?", confVar)
        i += 1

    for conf in confs:
        confVar = (confAbbrv[conf], conf)
        c.execute("UPDATE conference SET abbrv = ? WHERE name = ?", confVar)
        for team in confDict[conf]:
            teamVar = (confAbbrv[conf], team)
            c.execute("UPDATE team SET conference = ? WHERE name = ?", teamVar)

    conn.commit()
    conn.close()

if __name__ == "__main__": main()