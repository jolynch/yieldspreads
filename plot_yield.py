#!/usr/bin/python2.7
import urllib
from xml.dom.minidom import parse
from datetime import datetime
import dateutil.parser
import pprint
import numpy as np
import matplotlib.pyplot as plt


url = "http://data.treasury.gov/feed.svc/DailyTreasuryYieldCurveRateData"
print "Fetching XML from %s" % url
dom = parse(urllib.urlopen(url))
print " Done importing XML"
all_data = {}

#        <d:BC_1MONTH m:type="Edm.Double" m:null="true" />
#        <d:BC_3MONTH m:type="Edm.Double">5.190000057220459</d:BC_3MONTH>
#        <d:BC_6MONTH m:type="Edm.Double">5.3499999046325684</d:BC_6MONTH>
#        <d:BC_1YEAR m:type="Edm.Double">5.630000114440918</d:BC_1YEAR>
#        <d:BC_2YEAR m:type="Edm.Double">5.96999979019165</d:BC_2YEAR>
#        <d:BC_3YEAR m:type="Edm.Double">6.130000114440918</d:BC_3YEAR>
#        <d:BC_5YEAR m:type="Edm.Double">6.3000001907348633</d:BC_5YEAR>
#        <d:BC_7YEAR m:type="Edm.Double">6.4499998092651367</d:BC_7YEAR>
#        <d:BC_10YEAR m:type="Edm.Double">6.5399999618530273</d:BC_10YEAR>
#        <d:BC_20YEAR m:type="Edm.Double">6.8499999046325684</d:BC_20YEAR>
#        <d:BC_30YEAR m:type="Edm.Double">6.75</d:BC_30YEAR>

print "Parsing data from the XML"
for year in range(1990,datetime.now().year+1):
    all_data[year] = dict((i,[]) for i in [1,3,6,12,24,36,60,84,120,240,360])

tag_names = dict([(1,"d:BC_1MONTH"),
                  (3,"d:BC_3MONTH"),
                  (6,"d:BC_6MONTH"),
                  (12,"d:BC_1YEAR"),
                  (24,"d:BC_2YEAR"),
                  (36,"d:BC_3YEAR"),
                  (60,"d:BC_5YEAR"),
                  (84,"d:BC_7YEAR"),
                  (120,"d:BC_10YEAR"),
                  (240,"d:BC_20YEAR"),
                  (360,"d:BC_30YEAR")])
durations = tag_names.keys()

for node in dom.getElementsByTagName('entry'):
    data = node.getElementsByTagName('content')[0].getElementsByTagName('m:properties')[0]
    date = data.getElementsByTagName('d:NEW_DATE')[0].firstChild.nodeValue
    date = dateutil.parser.parse(date)
    if date.year in all_data:
        year_data = all_data[date.year]
        for dur in durations:
            if(data.getElementsByTagName(tag_names[dur])):
                xml_node = data.getElementsByTagName(tag_names[dur])[0]
                if xml_node.hasChildNodes():
                    year_data[dur].append(float(xml_node.firstChild.nodeValue))
print " Done parsing the data from the XML"
print "Generating Plots"
#for (year,spread) in all_data.items():
#    for dur in durations:
#        if spread[dur]:
#            spread[dur] = sum(spread[dur])/len(spread[dur])
#        else:
#            spread[dur] = None

def show_yield_curve(data,years):
    plt.figure()
    plt.xlabel('Duration (Months)')
    plt.ylabel('Yield (%)')
    plt.title("Yield Curves")
    for year in years:
        yield_curve = all_data[year]
        transformed = [(k,sum(v)/len(v)) for (k,v) in yield_curve.items() if k and v]
        transformed.sort(key=lambda x: x[0])
        x = [i for (i,j) in transformed]
        y = [j for (i,j) in transformed]
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
#show_yield_curve(all_data, all_data.keys())
show_spread(all_data, 3, 120)
#show_spread(all_data, 6, 120)
#show_spread(all_data, 6, 240)
plt.show()

print " Done generating plots"
