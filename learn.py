import numpy as np
import sqlite3
from sklearn import linear_model


def getdata(years, week, position, player = ""):
    '''
    Note: Years must be type tuple
    week: UP TO which week
    '''


    conn = sqlite3.connect('NFL.db')
    c = conn.cursor()
    week = range(week)
    week = tuple(week)

    if len(week) == 1:
        week = (0,0) #ugh

    #query that data that I want get all data for previous years + data for given number of weeks into current year
    c.execute('''select expts, hmdummy, rushyds, passyds
                 from final 
                 where (player = "{0}" 
                 and date in {1} 
                 and position = "{2}")
                 or (week in {3}
                 and player ="{0}"
                 and position = "{2}")'''.format(player, years, position, week))

    data = c.fetchall()
    
    pdata = []

    #turn the returned data into an np array
    for i in data:
        pdata.append(list(i))

    pdata = np.array(pdata)
    return pdata

#function for creating a regression for each individual player
#and putting it into a table

def regress(player, pdata):
    
    conn = sqlite3.connect("NFL.db")
    c = conn.cursor()

    if len(list(pdata)) >= 10:
        
        predictors = []

        y = pdata[:,0] #data not copied
        x = pdata[:,1:]

        for i in range(len(x[0])):  #center the predicters so the intercept is the player's  mean performance
            x[:,i] = x[:,i] - np.mean(x[:,i])
    
        clf = linear_model.LinearRegression()             
        clf.fit(x,y)

        predictors.append(player)
        predictors.append(clf.intercept_)
        for i in clf.coef_:
            predictors.append(i)
        predictors.append(np.std(y))
        predictors.append(clf.score(x,y))
        
        c.execute("insert into predict values (NULL,?,?,?,?,?,?,?,?,?)", predictors)
        conn.commit()
        conn.close()

    else:
        c.execute("insert into predict values (NUll,?,NULL,NULL,NULL,NULL,NULL,NULL,NULL, NULL)", [player])
        conn.commit()
        conn.close()

#now write a regression for all players and drop data into sql database
#definitely should have threaded this function....
def loopregress(years):

    conn = sqlite3.connect("NFL.db")
    c = conn.cursor()

    c.execute("select distinct(player), position from final group by player")
    players = c.fetchall()

    for player in players:
        data = getdata(player[0], years, 18, player[1])
        regress(player[0], data)

#loopregress((2010,2011,2012,2013,2014))

###predict start sits###

def predict(years, week, test = False):

    conn = sqlite3.connect("NFL.db")
    c = conn.cursor()

    #build a linear model with the following parameters...
    c.execute('''
              select expts, hmdummy, rushyds, passyds, av, week, pallow,
              dte, drb, dwr, dte*rushyds, dte*passyds,
              av*week, av*drb, dwr*week, dte*week, drb*week,
              dte*passyds, pallow*week, dwr*passyds, drb*passyds,
              rushyds*passyds, rushyds*pallow, dte*rushyds,
              dwr*passyds
              from final
              where (date in {0}
              or week < {1})
              '''.format(years, week))

    data = c.fetchall()

    data = np.array(data).astype(float)
    clf = linear_model.LinearRegression()
    y = data[:,0]
    x = data[:,1:] #ugly slicing...
    clf.fit(x,y)

    if test: #only test for the year 2014
        c.execute('''
              select expts, hmdummy, rushyds, passyds, av, week, pallow,
              dte, drb, dwr, dte*rushyds, dte*passyds,
              av*week, av*drb, dwr*week, dte*week, drb*week,
              dte*passyds, pallow*week, dwr*passyds, drb*passyds,
              rushyds*passyds, rushyds*pallow, dte*rushyds,
              dwr*passyds
              from final
              where date = 2014
              ''')

        tdata = c.fetchall()
        tdata = np.array(tdata).astype(float)

        ty = tdata[:,0]
        tx = tdata[:,1:]
        print clf.score(tx,ty)

        c.execute('''
              select expts, hmdummy, rushyds, passyds, av, week, pallow,
              dte, drb, dwr, dte*rushyds, dte*passyds,
              av*week, av*drb, dwr*week, dte*week, drb*week,
              dte*passyds, pallow*week, dwr*passyds, drb*passyds,
              rushyds*passyds, rushyds*pallow, dte*rushyds,
              dwr*passyds
              from final
              where date = 2014
              and player in (select distinct(player) from start)
              ''')

        tdata = c.fetchall()
        tdata = np.array(tdata).astype(float)

        ty = tdata[:,0]
        tx = tdata[:,1:]
        print clf.score(tx,ty)

    model = clf.fit(x,y)
        
    return model

predict((2010,2011,2012,2013),1, True)
        
def loopPredict(weeks = 18):
   
    conn = sqlite3.connect("NFL.db")
    c = conn.cursor()

    c.execute('''select distinct(start.player), position from start left join
                 final on start.player = final.player''') #get only the players that fabs discussed

    weeks = range(6,weeks) #just testing the weeks that I tested for fabiano
    qblist = []
    rblist = []
    telist = []
    wrlist = []

    players = c.fetchall()

    for week in weeks: #for each week from 6 to 17, although I will only analyze up to 15
                       # e.g. the end of the fantasy regular season
        fit = predict((2010,2011,2012,2013), week)
        for player in players:
            c.execute('''
                      select hmdummy, rushyds, passyds, av, week, pallow,
                      dte, drb, dwr, dte*rushyds, dte*passyds,
                      av*week, av*drb, dwr*week, dte*week, drb*week,
                      dte*passyds, pallow*week, dwr*passyds, drb*passyds,
                      rushyds*passyds, rushyds*pallow, dte*rushyds,
                      dwr*passyds 
                      from final
                      where player = "{0}" 
                      and week = {1}
                      and year = 2014
                      '''.format(player[0],week))
            
            data = c.fetchall()
            if data:
                data = np.array(data[0]).astype(float)
                x = fit.decision_function(data)
        
                #shouldnt have to exclude xs at or below zero
                #but I only have data for players that scored points
                #each fantasy week (complete data are hidden behind
                #an nfl paywall
                if x > 0 and player[1] == "QB":
                    qblist.append([player[0],x,week, player[1]])

                elif x > 0 and player[1] == "TE":
                    telist.append([player[0],x,week, player[1]])  

                elif x > 0 and player[1] == "RB":
                    rblist.append([player[0],x,week, player[1]])

                elif x > 0 and player[1] == "WR":
                    wrlist.append([player[0],x,week, player[1]])      
        
        func = lambda st:st[1]

        qblist.sort(key = func)
        telist.sort(key = func)
        rblist.sort(key = func)
        wrlist.sort(key = func)

        full = [qblist, telist, rblist, wrlist]
        
        #from sorted list of projects create a top5 start, bottom5 sit list
        #for each week/position
        for each in full:
            for row in each[-5:]:
                values = ["n","Start", row[2], row[0]]
                c.execute("insert into mystart values (NULL, ?, ?, ?, ?)", values)

            for row in each[:6]:
                values = ["n", "Sit", row[2], row[0]]
                c.execute("insert into mystart values (NULL, ?, ?, ?, ?)", values)

       
        qblist, telist, rblist, wrlist = [], [], [], []
    conn.commit()
    conn.close()

#loopPredict()
