"""Handles data readin and preprocessing."""
from collections import namedtuple

import pandas as pd

from assumptions import HOURLY_WAGE, PKG_PRICES, PLANNED_HOURS

DateRange = namedtuple("DateRange", "start end")

TOTAL_TIME = 'Total Time (1)'
RELEVANT_COLUMNS = ['Date', 'Project', 'Package Number', 'Complexity', TOTAL_TIME]


def pkg_profit(pkg_price, pkg_hours, wage):
    return pkg_price - pkg_hours * wage


def load_timetracking_data(path):
    """Loading the data"""
    # first column has to be dates!!
    tt_data = pd.read_csv(path, parse_dates=[0])
    # There are about 3,5K (~10% of overall data) entries which we can't use
    # Also there are 1364 entries where the complexity field is null
    tt_data_filter = ((tt_data['Complexity'] != 'NotSpecified') &
                      (tt_data['Complexity'] != 'Special') & (~(tt_data['Complexity'].isnull())))
    tt_data = tt_data[tt_data_filter]
    tt_data = tt_data.drop_duplicates()
    tt_data = tt_data.sort_values('Date')
    tt_data = tt_data[RELEVANT_COLUMNS]
    # Rename some columns for easier plotting
    tt_data = tt_data.rename(columns={'Date': 'x', 'Package Number': 'Pkg_ID'})

    tt_data['Price'] = tt_data['Complexity'].apply(lambda cpl: PKG_PRICES.value[cpl])

    tt_data['y'] = pkg_profit(tt_data["Price"], tt_data[TOTAL_TIME], HOURLY_WAGE.value)

    tt_data['planned_y'] = pkg_profit(
        tt_data['Price'], tt_data['Complexity'].apply(lambda cpl: PLANNED_HOURS.value[cpl]),
        HOURLY_WAGE.value)
    return tt_data


def tt_subset(data: pd.DataFrame, complexity_type: str, date_range: tuple):
    """Most used filter to subset data."""
    return ((data['Complexity'] == complexity_type) & (data['x'] > date_range.start) &
            (data['x'] < date_range.end))
