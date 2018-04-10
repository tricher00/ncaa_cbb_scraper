import pandas as pd

def main():
    years = [2012, 2013, 2014, 2015, 2016, 2017]
    df = pd.DataFrame(columns = ['Player', 'Year', 'PPG', 'RPG', 'SPG', 'BPG', 'ASTO', 'TS', 'SOS', 'VORP']);

    for year in years:
        players = []
        college = pd.read_csv("college{}.csv".format(year))
        nba = pd.read_csv("nbaRookies{}.csv".format(year+1))
        nba = nba[nba["Games"]>= 41]
        college = college[college["Games"] >= 15]

        nbaPlayers = nba["Player"].tolist()
        for x in nbaPlayers:
            if x in college["Player"].tolist():
                players.append(x)
        for player in players:
            nbaSeries = nba[nba["Player"] == player]
            collegeSeries = college[college["Player"] == player]
            #print nbaSeries
            #print collegeSeries
            data = {
                'Player': player,
                'Year' : year,
                'PPG' : collegeSeries.PPG.values[0],
                'RPG' : collegeSeries.RPG.values[0],
                'SPG' : collegeSeries.SPG.values[0],
                'BPG' : collegeSeries.BPG.values[0],
                'ASTO' : collegeSeries.Asists.values[0]/(collegeSeries.TPG.values[0] * collegeSeries.Games.values[0]),
                'TS' : collegeSeries['TS%'].values[0],
                'SOS' : collegeSeries.SOS.values[0],
                'VORP' : nbaSeries.VORP.values[0]
            }
            df = df.append(pd.Series(data), ignore_index = True)
            
    df.to_csv("collegeStatsAndVorp")
if __name__ == "__main__": main()