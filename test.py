#import sys
from bs4 import BeautifulSoup
import requests
import pandas as pd

def main():
    page = requests.get("https://www.sports-reference.com/cbb/boxscores/2017-11-23-stanford.html")
    boxSoup = BeautifulSoup(page.content, 'html.parser')
    box = boxSoup.find_all('table', id='box-score-basic-florida')
    test = box[0]
    
    headers = test.select("thead th")
    headers = headers[2:]
    colHeads = []
    for h in headers: colHeads.append(h.get_text())
    colHeads = [h.encode("utf-8") for h in colHeads]
    colHeads[0] = 'Name'
    df = pd.DataFrame(columns=colHeads)
    
    rows = test.select("tbody tr")
    rows.remove(rows[5])

    for row in rows:
        line = []
        name = row.select("th")[0].get_text().encode('utf-8')
        line.append(name)
        data = row.select('td')
        for x in data:
            line.append(x.get_text().encode("utf-8"))
        series = pd.Series(line,colHeads)
        df = df.append([series], ignore_index=True)
        
    df.to_csv("test.csv")
        
if __name__ == "__main__": main()
                