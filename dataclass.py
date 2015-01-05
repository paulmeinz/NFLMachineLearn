import numpy
import sqlite3

class squery():

    def __init__(self, to):
        self.to = to


    def poopout(self):
        return self.to


butt = squery(234)
print butt.poopout()
