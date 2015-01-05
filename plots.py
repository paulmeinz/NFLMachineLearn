import sqlite3
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt

conn = sqlite3.connect('NFL.db')
c = conn.cursor()

c.execute("select expts, av from final where year in (2010,2011,2012,2013) and av != 0")
data = c.fetchall()

data = np.array(data).astype(float)
data = pd.DataFrame(data, columns = ["Fantasy Points", "Previous Performance"])

p = sns.lmplot("Previous Performance", "Fantasy Points", data, ci = 95,
           scatter_kws = {"marker": ".", "color": "slategray"},
           line_kws = {"linewidth": 1, "color": "seagreen"})

p.set(xlim = (0,50), ylim = (0,50))

plt.show()
plt.clf()

