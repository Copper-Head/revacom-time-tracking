from collections import namedtuple
from datetime import datetime
from functools import partial

from bokeh.layouts import layout, widgetbox
from bokeh.models.widgets import Slider, Select, DateRangeSlider, Div
from bokeh.io import curdoc

from ttplotter import generate_plot, update
from datawrangler import load_timetracking_data, tt_subset, COST_COL, PROFIT_COL
from assumptions import COMPLEXITY_TYPES, assumption_html
from dateranger import date_range_from_request

DEFAULT_COMPLEXITY = "Basic"

tt_data = load_timetracking_data('/data/time_tracking.csv')
date_range = date_range_from_request(tt_data['x'].min(), tt_data['x'].max())
default_filter = tt_subset(tt_data, DEFAULT_COMPLEXITY, date_range)
default_data = tt_data[default_filter]
p1 = generate_plot(default_data, PROFIT_COL)
p2 = generate_plot(default_data, COST_COL)

# Bokeh page

Controls = namedtuple("Controls", "date complexity_type project rolling_window")
controls = Controls(
    date=DateRangeSlider(
        title='Dates',
        start=tt_data['x'].min(),
        end=tt_data['x'].max(),
        value=date_range,
        name='date-ranger'),
    complexity_type=Select(
        title='Package Complexity', value=DEFAULT_COMPLEXITY, options=COMPLEXITY_TYPES.value),
    project=Select(
        title='Project ID', value="All", options=['All'] + list(tt_data['Project'].unique())),
    rolling_window=Slider(title='Rolling Mean Window', start=5, end=500, value=100, step=1))


def multiplot_update(data, plots: list):
    """Create a callback that updates multiple plots from the same control values."""

    def callback(*controls):
        ctr_vals = [c.value for c in controls]
        for p in plots:
            update(p, data, *ctr_vals)

    return callback


update_callback = multiplot_update(tt_data, [p1, p2])
for ctrl in controls:
    # yapf: disable
    ctrl.on_change('value', lambda attr, old, new: update_callback(*controls))
    # yapf: disable

sizing_mode = 'fixed'
inputs = widgetbox(*controls, sizing_mode="stretch_both")
assumption_div = Div(text=assumption_html())

l = layout(
    [[inputs, p1],
    [assumption_div, p2]],
)
curdoc().add_root(l)
curdoc().title = "Package stats"
