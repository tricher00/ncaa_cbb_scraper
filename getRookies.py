from bs4 import BeautifulSoup
from bs4 import Comment
import requests
import re
import pandas as pd

def main():
    years = [2012, 2013, 2014, 2015, 2016, 2017, 2018]

    for year in years:
    
        url = "https://www.basketball-reference.com/leagues/NBA_{}_rookies.html".format(year)
        page = requests.get(url)
        bs = BeautifulSoup(page.content, 'html.parser')

        tbl = bs.find('table', {"id": "rookies"})
        tbody = tbl.find('tbody')
        rows = tbody.find_all('tr', {'class': 'full_table'})

        rookUrl = []
        rookNames = []
        games = []
        vorps = []
        for row in rows:
            player = row.find('td', {'data-stat':'player'})
            rookNames.append(player.find('a').get_text())
            rookUrl.append(player.find('a')['href'].encode('utf-8'))

        for rook in rookUrl:
            print rook
            rookAddress = "https://www.basketball-reference.com/" + rook
            rookPage = requests.get(rookAddress)
            rookBs = BeautifulSoup(rookPage.content, 'html.parser')
            perGame = rookBs.find("table", {"id":"per_game"})
            gp = perGame.find("td", {"data-stat":"g"}).get_text()
            games.append(gp)
            comments=rookBs.find_all(string=lambda text:isinstance(text,Comment))
            for x in comments:
                if 'vorp' in x.encode('utf-8'):
                    try:
                        regex = '<tr id="advanced\.{}.*?<td class="right " data-stat="vorp" >(.*?)<'.format(year)
                        z = re.search(regex, x.encode('utf-8'))
                        vorp = z.group(1)
                        break
                    except:
                        if 'vorp' not in vars():
                            vorp = ""
            vorps.append(vorp)
            
        print games
        print "{}: {}".format(rookNames[0], vorps[0])

        df = pd.DataFrame(
            {
                'Year': [year] * len(rookNames),
                'Player' : rookNames,
                'VORP' : vorps,
                'Games' : games
            }
            )
        df.to_csv("nbaRookies{}.csv".format(year))

if __name__ == "__main__": main()
    
