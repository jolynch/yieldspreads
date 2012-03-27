#!/usr/bin/python2.7
import urllib
from xml.dom.minidom import parse
from datetime import datetime
import dateutil.parser
import pprint
import numpy as np
import matplotlib.pyplot as plt

def parse_xml_from_url(url, into):
    print>>sys.stderr, "Fetching XML from %s" % url
    dom = parse(urllib.urlopen(url))
    print>>sys.stderr,  "Done parsing XML"
    all_data = {}

    tag_names =
        [
            "d:BC_1MONTH",
            "d:BC_3MONTH",
            "d:BC_6MONTH",
            "d:BC_1YEAR",
            "d:BC_2YEAR",
            "d:BC_3YEAR",
            "d:BC_5YEAR",
            "d:BC_7YEAR",
            "d:BC_10YEAR",
            "d:BC_20YEAR",
            "d:BC_30YEAR"
        ]

    for node in dom.getElementsByTagName('entry'):
        data = node.getElementsByTagName('content')[0].getElementsByTagName('m:properties')[0]
        date = data.getElementsByTagName('d:NEW_DATE')[0].firstChild.nodeValue
        date = dateutil.parser.parse(date)
        row = [date.date()]
        for dur in durations:
            if(data.getElementsByTagName(tag_names[dur])):
                xml_node = data.getElementsByTagName(tag_names[dur])[0]
                if xml_node.hasChildNodes():
                    row.append(round(float(xml_node.firstChild.nodeValue), 2))
                else:
                    row.append(None)
        writer.writerow(row)

if __name__ == "__main__":
    url = "http://data.treasury.gov/feed.svc/DailyTreasuryYieldCurveRateData"
    all_data = parse_xml_from_url(url, sys.stdout) 
