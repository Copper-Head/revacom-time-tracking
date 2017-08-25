import pandas as pd
import numpy as np

from bokeh.plotting import figure
from bokeh.layouts import layout, widgetbox
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.models.widgets import Slider, Select
from bokeh.io import curdoc

# Loading the data
# TODO: where do we get data from?
tt_data = pd.read_csv('/data/time_tracking.csv', parse_dates=[0], index_col=[0])
# For now drop duplicates. Would be nice to investigate where these are coming from
tt_data = tt_data.drop_duplicates()
# sort everything by date
tt_data = tt_data.sort_index(0)
# To make life easier later, store column name for total packaging time as a constant
TOTAL_TIME = 'Total Time (1)'

# This is all static for now until we get access to the actual data
# The prices came from Mathias
package_prices = {"Basic": 100, "Easy": 180, "Medium": 360, "Complex": 680}

planned_times = {"Basic": 2, "Easy": 4, "Medium": 8, "Complex": 16}

# Also static for now, pending us figuring something nicer out later
HOURLY_WAGE = 18


# Defining the plot
def _hline(y_value, x_values):
    """Generates a horizontal line by repeating y_value."""
    return np.repeat(y_value, len(x_values))


def pkg_profit(pkg_price, pkg_hours, wage):
    return pkg_price - pkg_hours * wage


p = figure(
        x_axis_type="datetime",
        # plot_height=height,
        # plot_width=width,
        active_scroll='wheel_zoom',
        title="Package Stats",
        title_location='above')

default_data = tt_data[tt_data['Complexity'] == "Basic"]
xs = default_data.index.values
tt = pkg_profit(package_prices["Basic"], default_data[TOTAL_TIME], HOURLY_WAGE)

source = ColumnDataSource(
    dict(
        x=xs, y=tt, proj=default_data['Project'], pkg_id=default_data['Package Number']))

p.scatter('x', 'y', name='datapoints', source=source, legend="Total Time")

p.line(
    xs,
    tt.rolling(
        100, min_periods=1).mean(),
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
    _hline(
        pkg_profit(package_prices['Basic'], planned_times['Basic'], HOURLY_WAGE),
        xs),
    line_color='green',
    name='planned',
    legend='Planned Profit',
    line_width=2)

p.add_tools(HoverTool(tooltips=[("Project", "@proj"), ('Package Number', '@pkg_id')]))


# Bokeh page

complexity_type = Select(
    title='Package Complexity', value="Basic", options=["Basic", "Easy", "Medium", "Complex"])
project = Select(
    title='Project ID', value="All", options=['All'] + list(tt_data['Project'].unique()))
rolling_window = Slider(title='Rolling Mean Window', start=5, end=500, value=100, step=1)


def update(plot):
    pkg_filter = (tt_data['Complexity'] == complexity_type.value)
    if project.value is not 'All':
        pkg_filter = pkg_filter & (tt_data['Project'] == project.value)

    this_complexity = tt_data[pkg_filter]
    new_x = this_complexity.index.values
    new_tt = pkg_profit(package_prices[complexity_type.value], this_complexity[TOTAL_TIME],
                        HOURLY_WAGE)

    plot.select_one("datapoints").data_source.data = {
        'x': new_x,
        'y': new_tt,
        'proj': this_complexity['Project'],
        'pkg_id': this_complexity['Package Number']
    }
    plot.select_one("rolling-mean").data_source.data = {
        'x': new_x,
        "y": new_tt.rolling(
            rolling_window.value, min_periods=1).mean()
    }
    plot.select_one('planned').data_source.data = {
        "x": new_x,
        "y": _hline(
            pkg_profit(package_prices[complexity_type.value], planned_times[complexity_type.value],
                       18), new_x)
    }
    plot.select_one("mean").data_source.data = {"x": new_x, "y": _hline(new_tt.mean(), new_x)}


controls = [complexity_type, project, rolling_window]
for control in controls:
    control.on_change('value', lambda attr, old, new: update(p))

sizing_mode = 'fixed'  # try 'scale_width' sometime?

inputs = widgetbox(*controls, sizing_mode=sizing_mode)
l = layout([[inputs, p]], sizing_mode=sizing_mode)

curdoc().add_root(l)
curdoc().title = "Package stats"
