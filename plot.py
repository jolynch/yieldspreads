#!/usr/bin/python2.7
import urllib
from xml.dom.minidom import parse
from datetime import datetime
from itertools import groupby
import dateutil.parser
import pprint
import numpy as np
import matplotlib.pyplot as plt
import csv
import sys
from decimal import *

columns = [1, 3, 6, 12, 24, 36, 60, 84, 120, 240, 360]

def analyze_data(data):
    year = lambda i: int(i[0][0:4])
    lines = [i for i in data]
    grouped_years = groupby(lines, year)
    out = {}
    for (year, d) in grouped_years:
        out[year] = [] 
        for (duration, yields) in zip(columns, np.array(list(d)).T[1:]):
            numeric_yields = [float(i) for i in yields if len(i) > 0]
            if len(numeric_yields) > 0:
                out[year].append((duration, sum(numeric_yields) / len(numeric_yields)))
    return out
        

def show_yield_curve(data):
    plt.figure()
    plt.xlabel('Duration (Months)')
    plt.ylabel('Yield (%)')
    plt.title("Yield Curves")
    for year in data:
        x = [duration for (duration,y) in data[year]]
        y = [y for (duration,y) in data[year]]
        plt.plot(x,y, label="%i"%year)
    plt.legend()

def show_spread(data, start, stop):
    x_data, y_data = [], []
    median_yield = []
    for (year, yields) in data.items():
        if(start in yields and stop in yields):
            if yields[start] and yields[stop]:
                x_data.append(year)
                spread = [yields[stop][i] - yields[start][i] for i in range(min(len(yields[start]), len(yields[stop])))]
                y_data.append(spread)
                median_yield.append(np.median(spread)) 
            #y_data.append(yields[stop]-yields[start])
    plt.figure()
    plt.xlabel('Year')
    plt.ylabel('%i to %i month yield spread' % (start,stop))
    plt.title('Yield Spread from Month %i to Month %i' % (start,stop))
    plt.plot(x_data, [np.mean(median_yield) for i in median_yield])    
    plt.boxplot(y_data)
    plt.setp(plt.gca(), 'xticklabels', ["\'"+str(x)[2:] for x in x_data] )

if __name__ == "__main__":
    all_data = analyze_data(csv.reader(sys.stdin))
    print(all_data[1990])
    
    show_yield_curve(all_data)
    #show_spread(all_data, 3, 120)
    #show_spread(all_data, 6, 120)
    #show_spread(all_data, 6, 240)
    plt.show()
    print " Done generating plots"
