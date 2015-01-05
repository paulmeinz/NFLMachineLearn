import requests
import bs4
import re
import sqlite3
import csv
import threading

#function for scraping data from footballdb.com (only provides non zero
#scores for a week)
def scrapeData(url):

    listofdata = []

    page = requests.get(url)
    soup = bs4.BeautifulSoup(page.text)

    for tr in soup.select("tr"):
        templist = []
        for tds in tr.find_all("td"):
            templist.append(tds.text) #extract data from all cells

        listofdata.append(templist)
    
    listofdata[-28:] = [] #28 rows describing scoring
    listofdata[0:2] = [] #two garbage rows
    #some additional munging, want to have team away/home
    for row in listofdata:
        
        if row[2][0] == '@':
            row.append('Away')
            row[2] = row[2][1:]

        else:
            row.append('Home')

    return listofdata

#function that gathers data for each play (aside from kickers/defense)
#by looping the previous function with new urls and puts into sql database.

def loopScrapeData(dates):
    """
    param dates: list of dates in int format
    """

    conn = sqlite3.connect('NFL.db')
    c = conn.cursor()

    if type(dates[0]) != int:
        return "dates must be of type int"

    weeks = range(1,18)
    positions = ["QB", "RB", "WR", "TE"]
    url = "http://www.footballdb.com/fantasy-football/index.html?pos={0}&yr={1}&wk={2}&ppr="

    listofdata = []

    for date in dates:

        for week in weeks:

            for position in positions:

                nurl = url.format(position, date, week)      
                data = scrapeData(nurl)

                for row in data:
                    row.append(week)
                    row.append(date)
                    row.append(position)
                    listofdata.append(row)
       
    c.executemany("insert into fantasy values (NULL,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",listofdata)
    conn.commit()
    conn.close()

###Get defense data and put it into sql database

##gotta convert teamnames from the defense table into three letter names for joins
def teamConvert(teamname):

    #Kind of like a javascript switch statement...

    team = {'Seattle Seahawks': 'Sea', 'Detroit Lions': 'Det', 'Buffalo Bills': 'Buf',
            'Denver Broncos': 'Den', 'San Francisco 49ers': 'SF', 'New York Jets': 'NYJ',
            'Kansas City Chiefs': 'KC', 'Baltimore Ravens': 'Bal', 'San Diego Chargers': 'SD',
            'Indianapolis Colts': 'Ind', 'Carolina Panthers': 'Car', 'Miami Dolphins': 'Mia',
            'New England Patriots': 'NE', 'Minnesota Vikings': 'Min', 'Houston Texans': 'Hou',
            'Green Bay Packers': 'GB', 'Oakland Raiders': 'Oak', 'St. Louis Rams': 'Stl',
            'Pittsburgh Steelers': 'Pit', 'Dallas Cowboys': 'Dal', 'Washington Redskins': 'Was',
            'Cincinnati Bengals': 'Cin', 'Cleveland Browns': 'Cle', 'Arizona Cardinals': 'Ari',
            'Tampa Bay Buccaneers': 'TB', 'Jacksonville Jaguars': 'Jac', 'Philadelphia Eagles': 'Phi',
            'New York Giants': 'NYG', 'Chicago Bears': 'Chi', 'New Orleans Saints': 'NO',
            'Atlanta Falcons': 'Atl', 'Tennessee Titans': 'Ten'}

    if teamname in team.viewkeys():
        return team[teamname]
    
    else:
        return "NONE"

def defScrapeFunc(years):
    """
    param years: LIST of years
    """

    conn = sqlite3.connect('NFL.db')
    c = conn.cursor()

    url = 'http://www.footballdb.com/fantasy-football/index.html?pos=DST&yr={0}&wk={1}&ppr='
    weeks = range(1,18)
    listofdata = []

    for year in years:
        for week in weeks:    
            newurl = url.format(year, week)
            page = requests.get(newurl)
            soup = bs4.BeautifulSoup(page.text)

            trs = soup.select("tr")

            for tr in trs:
                templist = []
                for td in tr.find_all("td"):
                    templist.append(td.text)
            
                if templist:    
                    templist.append(year)
                    templist.append(week)
                    templist.insert(0, teamConvert(templist[0]))
                    templist[1:2] = []
                    if templist[0] != "NONE":
                        listofdata.append(templist)

    c.executemany("insert into defense values (NULL,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",listofdata)
    conn.commit()
    conn.close()





####threading class to speed up the process

class Mythread(threading.Thread):
    def __init__(self, years):
        threading.Thread.__init__(self)

        self.years = years

    def run(self):
        #loopScrapeData(self.years)
        defScrapeFunc(self.years)
        print "Complete"
