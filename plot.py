#!/usr/bin/python2.7
import urllib
from itertools import groupby, islice, dropwhile
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

def show_spread(nly, spreads, yields):
    years    = mdates.YearLocator()   # every year
    months   = mdates.MonthLocator()  # every month
    yearsFmt = mdates.DateFormatter('%Y')

    fig = plt.figure()
    ax = fig.add_subplot(111)

    x = [date for (date, spread, funds) in spreads]
    y_s = [spread for (date, spread, funds) in spreads]
    y_f = [funds for (date, spread, funds) in spreads]
    ax.plot(x, y_s)
    ax.plot(x, y_f)
    ax.set_ylim(-2, 12)
    
    nly_x, nly_y = [], []

    for i in nly:
        nly_x.append(dateutil.parser.parse(i[0]))
        nly_y.append(float(i[1]))
    
    ax2 = ax.twinx()
    axis_color = 'r'
    ax2.plot(nly_x, nly_y, axis_color, linewidth=0.5)
    ax2.set_ylabel('NLY price', color=axis_color)
    for tl in ax2.get_yticklabels():
        tl.set_color(axis_color)
    ax2.set_ylim(0, 23)

    x = [date for (date, y) in yields]
    y = [y for (date, y) in yields]
    print y
    ax2.scatter(x, y)

    ax.xaxis.set_major_locator(years)
    ax.xaxis.set_major_formatter(yearsFmt)
    ax.xaxis.set_minor_locator(months)

    datemin = datetime.date(2005, 1, 1)
    datemax = datetime.date(2013, 1, 1)
    ax.set_xlim(datemin, datemax)

    ax.grid(True)
    fig.autofmt_xdate()

    plt.xlabel('Year')
    plt.ylabel('Yield spread')
    plt.title('Yield spread')
    plt.show()

if __name__ == "__main__":
    #argv[1] -> "funds rate"
    #argv[2] -> "mortgage rate"
    #argv[3] -> "price"

    transform = lambda i: (dateutil.parser.parse(i[0]), float(i[1]))
    daterange = lambda i: i[0].year >= 1997
    funds = [transform(i) for i in csv.reader(open(sys.argv[1]))]
    funds = filter(daterange, funds)
    mortgage = [transform(i) for i in csv.reader(open(sys.argv[2]))]
    mortgage = filter(daterange, mortgage)

    def continuator(l): #a generator which fills in the gaps between data points
        tail = islice(l, 1, None)
        for (f, t) in zip(l, tail):
            value = f[1]
            start = f[0]
            end = t[0]
            for n in range((end - start).days):
                yield (start + datetime.timedelta(n), value)
        yield l[-1]

    start = max(funds[0][0], mortgage[0][0])
    prestart = lambda i: i[0] < start
    funds = dropwhile(prestart, continuator(funds))
    mortgage = dropwhile(prestart, continuator(mortgage))

    spreads = [(f[0], m[1] - f[1], f[1]) for (f, m) in zip(funds, mortgage)]

    c = 4 # <- the holy constant of made-upness
    nly = [(i[0], float(i[1])) for i in csv.reader(open(sys.argv[3]))]
    price_lookup = dict(nly) #HACK!
    yields = [(dateutil.parser.parse(i[0]), c * 100 * float(i[1])/price_lookup[i[0]]) for i in csv.reader(open(sys.argv[4]))]
    
    #show_yield_curve(all_data)
    show_spread(nly, spreads, yields)
    #show_spread(all_data, 6, 120)
    #show_spread(all_data, 6, 240)
