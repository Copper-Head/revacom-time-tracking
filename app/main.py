from collections import namedtuple

import pandas as pd

from bokeh.layouts import layout, widgetbox
from bokeh.models.widgets import Slider, Select
from bokeh.io import curdoc

from ttplotter import generate_plot, update

# Loading the data
# TODO: where do we get data from?
tt_data = pd.read_csv('/data/time_tracking.csv', parse_dates=[0])
# There are about 3,5K (~10% of overall data) entries which we can't use
# Also there are 1364 entries where the complexity field is null
tt_data_filter = ((tt_data['Complexity'] != 'NotSpecified')
                  & (tt_data['Complexity'] != 'Special')
                  & (~(tt_data['Complexity'].isnull())))
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
# Also static for now, pending us figuring something nicer out later
HOURLY_WAGE = 18


def pkg_profit(pkg_price, pkg_hours, wage):
    return pkg_price - pkg_hours * wage


tt_data['y'] = pkg_profit(tt_data["Price"], tt_data[TOTAL_TIME], HOURLY_WAGE)

planned_times = {"Basic": 2, "Easy": 4, "Medium": 8, "Complex": 16}
tt_data['planned_y'] = pkg_profit(tt_data['Price'],
                                  tt_data['Complexity'].apply(lambda cpl: planned_times[cpl]),
                                  HOURLY_WAGE)

default_data = tt_data[tt_data['Complexity'] == "Basic"]
p = generate_plot(default_data)

# Bokeh page

Controls = namedtuple("Controls", "complexity_type project rolling_window")
controls = Controls(
    complexity_type=Select(
        title='Package Complexity', value="Basic", options=["Basic", "Easy", "Medium", "Complex"]),
    project=Select(
        title='Project ID', value="All", options=['All'] + list(tt_data['Project'].unique())),
    rolling_window=Slider(
        title='Rolling Mean Window', start=5, end=500, value=100, step=1))

for name, control in controls._asdict().items():
    control.on_change('value',
                      lambda attr, old, new: update(p, tt_data, * [c.value for c in controls]))

sizing_mode = 'fixed'
inputs = widgetbox(*controls, sizing_mode=sizing_mode)

l = layout([[inputs, p]], sizing_mode=sizing_mode)
curdoc().add_root(l)
curdoc().title = "Package stats"
