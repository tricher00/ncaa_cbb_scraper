from bs4 import BeautifulSoup
import requests
import re

def main():
    url = "https://www.sports-reference.com/cbb/conferences/"
    page = requests.get(url)
    bs = BeautifulSoup(page.content, 'html.parser')

    tbl = bs.find('div', {"id":"all_active"})
    
    rows = tbl.find_all("tr") 
    rows = rows[1:len(rows)]
    
    regex = "/cbb/conferences/(.*)/\""
    conf = []
    abbrv = []
    for x in rows:
        a = x.find('a')
        conf.append(a.get_text())
        abbrv.append(re.search(regex,str(a)).group(1))

    confDict = {}

    for i in range(len(conf)):
        print conf[i]
        confDict[conf[i]] = []
        confUrl = url + "/{}/2018.html".format(abbrv[i])
        confPage = requests.get(confUrl)
        confBs = BeautifulSoup(confPage.content, 'html.parser')
        teams = confBs.findAll('td', {"data-stat":"school_name"})
        for team in teams:
            confDict[conf[i]].append(team.get_text())

    print confDict
        
if __name__ == "__main__": main()