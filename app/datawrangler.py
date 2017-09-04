"""Handles data readin and preprocessing."""
import pandas as pd

from assumptions import HOURLY_WAGE, PKG_PRICES, PLANNED_HOURS, COMPLEXITY_TYPES
from dateranger import DateRange

TOTAL_TIME = 'Total Time (1)'
RELEVANT_COLUMNS = ['Date', 'Project', 'Package Number', 'Complexity', TOTAL_TIME]
COST_COL = 'Costs'
PROFIT_COL = 'Profits'


def planned_col_name(metric_name):
    return "Planned{}".format(metric_name)


def load_timetracking_data(path):
    """Loading the data"""
    # first column has to be dates!!
    tt_data = pd.read_csv(path, parse_dates=[0])
    tt_data = tt_data[tt_data['Complexity'].isin(COMPLEXITY_TYPES.value)]
    # We noticed duplicate entries that only differed in the date they were entered.
    # We decided to remove such entries.
    tt_data = tt_data.drop_duplicates(subset=(set(tt_data) - set(['Date'])))
    tt_data = tt_data[RELEVANT_COLUMNS]
    # Rename some columns for easier plotting
    tt_data = tt_data.rename(columns={'Date': 'x', 'Package Number': 'Pkg_ID'})

    tt_data['Price'] = tt_data['Complexity'].apply(lambda cpl: PKG_PRICES.value[cpl])
    tt_data['PlannedTime'] = tt_data['Complexity'].apply(lambda cpl: PLANNED_HOURS.value[cpl])

    tt_data[COST_COL] = tt_data[TOTAL_TIME] * HOURLY_WAGE.value
    planned_cost_col = planned_col_name(COST_COL)
    tt_data[planned_cost_col] = tt_data['PlannedTime'] * HOURLY_WAGE.value
    tt_data[PROFIT_COL] = tt_data['Price'] - tt_data[COST_COL]
    tt_data[planned_col_name(PROFIT_COL)] = tt_data['Price'] - tt_data[planned_cost_col]

    return tt_data


def tt_subset(data: pd.DataFrame, complexity_type: str, date_range: DateRange):
    """Most used filter to subset data."""
    return ((data['Complexity'] == complexity_type) & (data['x'] > date_range.start) &
            (data['x'] < date_range.end))
