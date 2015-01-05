NFLMachineLearn
===============

Code I used to develop a machine learning algorith for predicting player fantasy football performance

NFL.db is a sqlite3 database of fantasy football data. I performed my analysis using the "final" table and variables
expts (fantasy points earned in a given week), date (year data were collected), week (football game week),
rushyds (avg rush yards allowed by defensive opponent up to previous week), passyds, pallow (avg points allowed
up to previous week), dte, dwr, drb (dummy variables for player position), and av (average previous performance
in fantasy points)

scrape.py is code for scraping nfl data for the last four years.
threadscrape.py just threads the scrape functions to speed things up.
learn.py is the learning algorithm development code.
plot.py is a simple regression plot.
R code is from a previous analysis (see NFLFantasyAnalysis)
