import requests
import bs4
import re
import sqlite3
import csv
import threading
import scrape as sc

g1 = [2010, 2011]
g2 = [2012]
g3 = [2013]
g4 = [2014]

one = sc.Mythread(g1)
two = sc.Mythread(g2)
three = sc.Mythread(g3)
four = sc.Mythread(g4)

one.start()
two.start()
three.start()
four.start()

