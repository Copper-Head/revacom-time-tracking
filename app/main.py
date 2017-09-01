from collections import namedtuple
from datetime import datetime

from bokeh.layouts import layout, widgetbox
from bokeh.models.widgets import Slider, Select, DateRangeSlider
from bokeh.io import curdoc

from ttplotter import generate_plot, update
from datawrangler import load_timetracking_data

DEFAULT_COMPLEXITY = "Basic"
DATE_FORMAT = "%d/%m/%Y"


def _convert(date: str, default: datetime.date) -> datetime.date:
    try:
        return datetime.strptime(date, DATE_FORMAT).date()
    except ValueError:
        return default


def _extract(request_arguments: dict, arg_name: str) -> str:
    return request_arguments.get(arg_name, [])[0].decode()


def _extract_start_end(request_arguments: dict) -> tuple:
    return _extract(request_arguments, "start"), _extract(request_arguments, "end")


def date_range_from_request(default_start, default_end) -> tuple:
    """Infer date range selection from request."""
    request_args = curdoc().session_context.request.arguments
    start, end = _extract_start_end(request_args)
    return _convert(start, default_start), _convert(end, default_end)


tt_data = load_timetracking_data('/data/time_tracking.csv')
date_range = date_range_from_request(tt_data['x'].min(), tt_data['x'].max())
default_filter = ((tt_data['Complexity'] == DEFAULT_COMPLEXITY) & (tt_data['x'] > date_range[0]) &
                  (tt_data['x'] < date_range[1]))
default_data = tt_data[default_filter]
p = generate_plot(default_data)

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
        title='Package Complexity',
        value=DEFAULT_COMPLEXITY,
        options=["Basic", "Easy", "Medium", "Complex"]),
    project=Select(
        title='Project ID', value="All", options=['All'] + list(tt_data['Project'].unique())),
    rolling_window=Slider(title='Rolling Mean Window', start=5, end=500, value=100, step=1))

for name, control in controls._asdict().items():
    control.on_change('value',
                      lambda attr, old, new: update(p, tt_data, * [c.value for c in controls]))

sizing_mode = 'fixed'
inputs = widgetbox(*controls, sizing_mode="stretch_both")

l = layout(
    [[inputs, p]],
    # sizing_mode="stretch_both"
)
curdoc().add_root(l)
curdoc().title = "Package stats"
