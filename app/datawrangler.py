"""Handles data readin and preprocessing."""
from collections import namedtuple

import pandas as pd

from assumptions import HOURLY_WAGE

DateRange = namedtuple("DateRange", "start end")


def pkg_profit(pkg_price, pkg_hours, wage):
    return pkg_price - pkg_hours * wage


def load_timetracking_data(path):
    """Loading the data"""
    tt_data = pd.read_csv(path, parse_dates=[0])
    # There are about 3,5K (~10% of overall data) entries which we can't use
    # Also there are 1364 entries where the complexity field is null
    tt_data_filter = ((tt_data['Complexity'] != 'NotSpecified') &
                      (tt_data['Complexity'] != 'Special') & (~(tt_data['Complexity'].isnull())))
    tt_data = tt_data[tt_data_filter]
    # For now drop duplicates. Would be nice to investigate where these are coming from
    tt_data = tt_data.drop_duplicates()
    # sort everything by date
    tt_data = tt_data.sort_values('Date')
    # To make life easier later, store column name for total packaging time as a constant
    TOTAL_TIME = 'Total Time (1)'
    # Only use subset of columns
    tt_data = tt_data[['Date', 'Project', 'Package Number', 'Complexity', TOTAL_TIME]]
    tt_data = tt_data.rename(columns={'Date': 'x', 'Package Number': 'Pkg_ID'})

    # This is all static for now until we get access to the actual data
    # The prices came from Mathias
    package_prices = {"Basic": 100, "Easy": 180, "Medium": 360, "Complex": 680}
    tt_data['Price'] = tt_data['Complexity'].apply(lambda cpl: package_prices[cpl])

    tt_data['y'] = pkg_profit(tt_data["Price"], tt_data[TOTAL_TIME], HOURLY_WAGE.value)

    planned_times = {"Basic": 2, "Easy": 4, "Medium": 8, "Complex": 16}
    tt_data['planned_y'] = pkg_profit(tt_data['Price'],
                                      tt_data['Complexity'].apply(lambda cpl: planned_times[cpl]),
                                      HOURLY_WAGE.value)
    return tt_data


def tt_subset(data: pd.DataFrame, complexity_type: str, date_range: tuple):
    """Most used filter to subset data."""
    return ((data['Complexity'] == complexity_type) & (data['x'] > date_range.start) &
            (data['x'] < date_range.end))
