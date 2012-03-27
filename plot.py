#!/usr/bin/python2.7
import urllib
from xml.dom.minidom import parse
from itertools import groupby
import datetime
import matplotlib.dates as mdates
import dateutil.parser
import pprint
import numpy as np
import matplotlib.pyplot as plt
import csv
import sys
from decimal import *

columns = ["Year", 1, 3, 6, 12, 24, 36, 60, 84, 120, 240, 360]

def analyze_data(lines):
    year = lambda i: int(i[0][0:4])
    grouped_years = groupby(lines, year)
    out = {}
    for (year, d) in grouped_years:
        out[year] = dict() 
        for (duration, yields) in zip(columns[1:], np.array(list(d)).T[1:]):
            numeric_yields = [float(i) for i in yields if len(i) > 0]
            if len(numeric_yields) > 0:
                out[year][duration] = sum(numeric_yields) / len(numeric_yields)
    return out
        

def show_yield_curve(data):
    plt.figure()
    plt.xlabel('Duration (Months)')
    plt.ylabel('Yield (%)')
    plt.title("Yield Curves")
    for year in data:
        t = sorted([i for i in data[year].items()], key=(lambda (k,v): k))

        x = [duration for (duration,y) in t]
        y = [y for (duration,y) in t]
        plt.plot(x,y, label="%i"%year)
    plt.legend()

def show_spread(data, nly, up, down):

    years    = mdates.YearLocator()   # every year
    months   = mdates.MonthLocator()  # every month
    yearsFmt = mdates.DateFormatter('%Y')

    fig = plt.figure()
    ax = fig.add_subplot(111)

    x_data, spread_y, down_y = [], [], []
    median_yield = []
    up_pos = columns.index(up)
    down_pos = columns.index(down)
    for l in data:
        day = dateutil.parser.parse(l[0])
        up_val = l[up_pos]
        down_val = l[down_pos]

        if len(up_val) > 0 and len(down_val) > 0:
            x_data.append(day)
            d = float(down_val)

            down_y.append(d)
            spread_y.append(float(up_val) - d)

    ax.plot(x_data, down_y)
    ax.plot(x_data, spread_y)
    
    nly_x, nly_y = [], []

    for i in nly:
        nly_x.append(dateutil.parser.parse(i[0]))
        nly_y.append(float(i[6]))

    ax.plot(nly_x, nly_y)

    ax.xaxis.set_major_locator(years)
    ax.xaxis.set_major_formatter(yearsFmt)
    ax.xaxis.set_minor_locator(months)

    datemin = datetime.date(min(nly_x).year, 1, 1)
    datemax = datetime.date(max(nly_x).year + 1, 1, 1)
    ax.set_xlim(datemin, datemax)

    ax.grid(True)
    fig.autofmt_xdate()

    plt.xlabel('Year')
    plt.ylabel('%i to %i month yield spread' % (up,down))
    plt.title('Yield Spread from Month %i to Month %i' % (up,down))
    plt.show()

if __name__ == "__main__":
    
    all_data = [i for i in csv.reader(sys.stdin) if i[0][0:4]>="1997"]
    nly = [i for i in csv.reader(open("NLY.csv"))]
    
    #show_yield_curve(all_data)
    show_spread(all_data, nly, 120, 3)
    #show_spread(all_data, 6, 120)
    #show_spread(all_data, 6, 240)
