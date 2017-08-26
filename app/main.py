from collections import namedtuple

import pandas as pd
import numpy as np

from bokeh.plotting import figure
from bokeh.layouts import layout, widgetbox
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.models.widgets import Slider, Select
from bokeh.io import curdoc

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
tt_data['planned_y'] = pkg_profit(tt_data['Price'], tt_data['Complexity'].apply(lambda cpl: planned_times[cpl]), HOURLY_WAGE)


# Defining the plot
def _hline(y_value, x_values):
    """Generates a horizontal line by repeating y_value."""
    return np.repeat(y_value, len(x_values))


p = figure(
    x_axis_type="datetime",
    # plot_height=height,
    # plot_width=width,
    active_scroll='wheel_zoom',
    title="Package Stats",
    x_axis_label='Time',
    y_axis_label='Profits (EUR)',
    title_location='above')

p.add_tools(HoverTool(tooltips=[("Project", "@Project"), ('Package Number', '@Pkg_ID')]))

default_data = tt_data[tt_data['Complexity'] == "Basic"]
xs = default_data['x']
tt = default_data['y']

source = ColumnDataSource.from_df(default_data)

p.scatter('x', 'y', name='datapoints', source=source, legend="Total Time")

# yapf:disable
p.line(
    xs,
    tt.rolling(100, min_periods=1).mean(),
    line_width=3,
    color='black',
    name='rolling-mean',
    legend='Running Average')
p.line(
    xs,
    _hline(tt.mean(), xs),
    line_color='red',
    name='mean',
    legend="Data Average",
    line_width=2)
p.line(
    xs,
    default_data['planned_y'],
    line_color='green',
    name='planned',
    legend='Planned Profit',
    line_width=2)
# yapf:enable


# Bokeh page


def _update_line(plot, line_name, new_x, new_y):
    plot.select_one(line_name).data_source.data = {'x': new_x, "y": new_y}


def _update_rolling_window(plot, new_x, new_tt, rolling_window):
    _update_line(plot, "rolling-mean", new_x, new_tt.rolling(rolling_window, min_periods=1).mean())


def _update_mean(plot, new_x, new_y):
    _update_line(plot, "mean", new_x, _hline(new_y.mean(), new_x))


def update(plot, complexity_type, project, rolling_window):
    pkg_filter = (tt_data['Complexity'] == complexity_type)
    if project is not 'All':
        pkg_filter = pkg_filter & (tt_data['Project'] == project)

    this_complexity = tt_data[pkg_filter]
    new_x = this_complexity['x']
    new_tt = this_complexity['y']

    plot.select_one("datapoints").data_source.data = ColumnDataSource.from_df(this_complexity)
    _update_line(plot, "planned", new_x, this_complexity['planned_y'])
    # These have to be recomputed every time
    _update_mean(plot, new_x, new_tt)
    _update_rolling_window(plot, new_x, new_tt, rolling_window)


Controls = namedtuple("Controls", "complexity_type project rolling_window")
controls = Controls(
    complexity_type=Select(
        title='Package Complexity', value="Basic", options=["Basic", "Easy", "Medium", "Complex"]),
    project=Select(
        title='Project ID', value="All", options=['All'] + list(tt_data['Project'].unique())),
    rolling_window=Slider(
        title='Rolling Mean Window', start=5, end=500, value=100, step=1))

for name, control in controls._asdict().items():
    control.on_change('value', lambda attr, old, new: update(p, * [c.value for c in controls]))

sizing_mode = 'fixed'
inputs = widgetbox(*controls, sizing_mode=sizing_mode)

l = layout([[inputs, p]], sizing_mode=sizing_mode)
curdoc().add_root(l)
curdoc().title = "Package stats"
