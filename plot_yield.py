#!/usr/bin/env python3

import urllib.request
from xml.dom.minidom import parseString
from datetime import datetime
import os
import pickle
from pathlib import Path
import dateutil.parser
import numpy as np
import matplotlib.pyplot as plt


def parse_xml_from_url(url):
    all_data = {}

    print(
        "Pulling data from the XML looking for data between 1990 and %i"
        % (datetime.now().year)
    )
    for year in range(1990, datetime.now().year + 1):
        all_data[year] = dict(
            (i, []) for i in [1, 3, 6, 12, 24, 36, 60, 84, 120, 240, 360]
        )

    tag_names = dict(
        [
            (1, "d:BC_1MONTH"),
            (3, "d:BC_3MONTH"),
            (6, "d:BC_6MONTH"),
            (12, "d:BC_1YEAR"),
            (24, "d:BC_2YEAR"),
            (36, "d:BC_3YEAR"),
            (60, "d:BC_5YEAR"),
            (84, "d:BC_7YEAR"),
            (120, "d:BC_10YEAR"),
            (240, "d:BC_20YEAR"),
            (360, "d:BC_30YEAR"),
        ]
    )
    durations = tag_names.keys()

    page = 0
    more = True
    print("Fetching XML in pages from %s" % url)
    while more:
        fetch = f"{url}&page={page}"
        print("Fetching XML from %s" % fetch)
        with urllib.request.urlopen(fetch) as fd:
            info = fd.read().decode("utf-8")
            dom = parseString(info)
        more = False
        for node in dom.getElementsByTagName("entry"):
            more = True
            data = node.getElementsByTagName("content")[0].getElementsByTagName(
                "m:properties"
            )[0]
            date = data.getElementsByTagName("d:NEW_DATE")[0].firstChild.nodeValue
            date = dateutil.parser.parse(date)
            if date.year in all_data:
                year_data = all_data[date.year]
                for dur in durations:
                    if data.getElementsByTagName(tag_names[dur]):
                        xml_node = data.getElementsByTagName(tag_names[dur])[0]
                        if xml_node.hasChildNodes():
                            year_data[dur].append(float(xml_node.firstChild.nodeValue))
        page = page + 1
    print("Done parsing the data from the XML")
    return all_data


def show_yield_curve(data, years):
    fig = plt.figure(figsize=(12, 8))
    plt.xlabel("Duration (Months)")
    plt.ylabel("Yield (%)")
    plt.title("Yield Curves")

    ax = fig.axes[0]
    colormap = plt.cm.nipy_spectral
    colors = [colormap(i) for i in np.linspace(0, 1, len(years))]
    ax.set_prop_cycle("color", colors)
    for year in years:
        yield_curve = all_data[year]
        transformed = [
            (k, sum(v) / len(v)) for (k, v) in yield_curve.items() if k and v
        ]
        transformed.sort(key=lambda x: x[0])
        x = [i for (i, j) in transformed]
        y = [j for (i, j) in transformed]
        plt.plot(x, y, label="%i" % year)
    plt.legend()


def show_spread(data, start, stop):
    x_data, y_data = [], []
    median_yield = []
    for (year, yields) in data.items():
        if start in yields and stop in yields:
            if yields[start] and yields[stop]:
                x_data.append(year)
                spread = [
                    yields[stop][i] - yields[start][i]
                    for i in range(min(len(yields[start]), len(yields[stop])))
                ]
                y_data.append(spread)
                median_yield.append(np.median(spread))
            # y_data.append(yields[stop]-yields[start])
    plt.figure(figsize=(14, 8))
    plt.xlabel("Year")
    plt.ylabel("%i to %i month yield spread" % (start, stop))
    plt.title("Yield Spread from Month %i to Month %i" % (start, stop))
    plt.plot(x_data, [np.mean(median_yield) for i in median_yield])
    plt.boxplot(y_data)
    plt.setp(plt.gca(), "xticklabels", ["'" + str(x)[2:] for x in x_data])
    plt.xlim([0, max(x_data) - min(x_data)])


def help():
    result = "  get_data      | gd         Get yield data\n"
    result += "  yield_spread  | ys         Show yield spread\n"
    result += "  yield_curve   | yc         Show yield curve\n"
    result += "  quit          | q          Quit"
    return result


if __name__ == "__main__":
    print("Welcome to YieldCurves!")
    plt.ion()
    all_data = {}
    cache = Path("./.spreads.dat")
    if cache.is_file():
        print("Loading cached data from .spreads.dat")
        with cache.open(mode="rb") as fd:
            try:
                all_data = pickle.load(fd)
            except Exception as exp:
                print("Error loading cached data: " + exp)
                all_data = {}
    while True:
        i = input("(yieldcurves) ")
        continue_through = False
        if i == "help" or i == "h":
            print(help())
        elif i == "get_data" or i == "gd":
            loc = input("Automatically fetch data from the Treasury website [y|n]: ")
            if loc == "y":
                url = (
                    "https://home.treasury.gov/resource-center/"
                    "data-chart-center/interest-rates/pages/"
                    "xml?data=daily_treasury_yield_curve"
                    "&field_tdr_date_value=all"
                )
                all_data = parse_xml_from_url(url)
                with cache.open(mode="wb") as fd:
                    pickle.dump(all_data, fd)
            elif loc == "n":
                loc = input("File location or url [file|url]: ")
                # TODO: Add the local file input code here
            else:
                pass
        elif i == "yield_spread" or i == "ys":
            if all_data:
                start = input(
                    "Starting maturity in months [1|3|6|12|24|36|60|84|120|240|360]: "
                )
                end = input(
                    "Ending maturity in months   [1|3|6|12|24|36|60|84|120|240|360]: "
                )
                try:
                    start, end = int(start), int(end)
                    show_spread(all_data, start, end)
                    plt.show()
                except Exception as exp:
                    print("Invalid input: " + exp)
            else:
                print("You need to get yield data before you can display it!")
        elif i == "yield_curve" or i == "yc":
            if all_data:
                years = input(
                    "Display a single year or multiple years [(s)ingle|(m)ultiple]: "
                )
                if years in ("single", "s"):
                    year = input("Which year: ")
                    try:
                        year = int(year)
                        show_yield_curve(all_data, [year])
                    except Exception as exp:
                        print("Invalid input: " + exp)
                elif years in ("multiple", "m"):
                    start_year = input("Start year: ")
                    end_year = input("End year: ")
                    try:
                        start_year, end_year = int(start_year), int(end_year)
                        years = range(start_year, end_year)
                        show_yield_curve(all_data, years)
                    except Exception as exp:
                        print("Invalid input: " + exp)
                else:
                    pass
            else:
                print("You need to get yield data before you can display it!")
        elif i == "quit" or i == "q":
            break
        else:
            continue
