from bs4 import BeautifulSoup
import requests
import re

def getConfs():
    url = "https://www.sports-reference.com/cbb/conferences/"
    page = requests.get(url)
    bs = BeautifulSoup(page.content, 'html.parser')

    year = "2011"

    tbl = bs.find('div', {"id":"all_active"})
    
    rows = tbl.find_all("tr") 
    rows = rows[1:len(rows)]
    
    confAbbrv = {}

    regex = "/cbb/conferences/(.*)/\""

    for x in rows:
        a = x.find('a')
        conf = a.get_text()
        abbrv = re.search(regex,str(a)).group(1)
        confAbbrv[conf] = abbrv

    confDict = {}
    nameRegex = "/cbb/schools/(.*)/"

    confs = confAbbrv.keys()

    for conf in confs:
        if conf == "American Athletic Conference" and year < 2014:
            continue
        confDict[conf] = []
        confUrl = url + "/{}/{}.html".format(confAbbrv[conf],year)
        confPage = requests.get(confUrl)
        confBs = BeautifulSoup(confPage.content, 'html.parser')
        teams = confBs.findAll('td', {"data-stat":"school_name"})
        for team in teams:
            teamLink = team.find('a')['href'].encode('utf-8')
            name = re.search(nameRegex, teamLink).group(1)
            confDict[conf].append(name)

    return [confDict, confAbbrv]