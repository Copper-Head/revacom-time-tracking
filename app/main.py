from collections import namedtuple

from bokeh.layouts import layout, widgetbox
from bokeh.models.widgets import Slider, Select
from bokeh.io import curdoc

from ttplotter import generate_plot, update
from datawrangler import load_timetracking_data

tt_data = load_timetracking_data('/data/time_tracking.csv')
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
