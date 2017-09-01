"""Houses plot generation and updating logic."""
from datetime import date

import numpy as np
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool

from datawrangler import DateRange, tt_subset


def _hline(y_value, x_values):
    """Generates a horizontal line by repeating y_value."""
    return np.repeat(y_value, len(x_values))


def _date_from_js(timestamp: int):
    """Borrowed from Bokeh's Date.transform method.

    After some poking around I discovered this works best with the values
    we get from the JS frontend when the slider is dragged.
    """
    if isinstance(timestamp, int):
        try:
            return date.fromtimestamp(timestamp)
        except ValueError:
            return date.fromtimestamp(timestamp / 1000)
    else:
        return timestamp


def generate_plot(data):
    """Create bokeh figure from some initial data."""
    plot = figure(
        x_axis_type="datetime",
        plot_width=900,
        active_scroll='wheel_zoom',
        title="Package Stats",
        x_axis_label='Time',
        y_axis_label='Profits (EUR)',
        title_location='above')

    plot.add_tools(HoverTool(tooltips=[("Project", "@Project"), ('Package Number', '@Pkg_ID')]))

    xs = data['x']
    tt = data['y']

    source = ColumnDataSource.from_df(data)

    plot.scatter('x', 'y', name='datapoints', source=source, legend="Total Time")

    # yapf:disable
    plot.line(
        xs,
        tt.rolling(100, min_periods=1).mean(),
        line_width=3,
        color='black',
        name='rolling-mean',
        legend='Running Average')
    plot.line(
        xs,
        _hline(tt.mean(), xs),
        line_color='red',
        name='mean',
        legend="Data Average",
        line_width=2)
    plot.line(
        xs,
        data['planned_y'],
        line_color='green',
        name='planned',
        legend='Planned Profit',
        line_width=2)
    # yapf:enable
    plot.legend.click_policy = "hide"
    return plot


def _update_line(plot, line_name, new_x, new_y):
    """Wrapper that updates a plot's line attribute by name."""
    plot.select_one(line_name).data_source.data = {'x': new_x, "y": new_y}


def _update_rolling_window(plot, new_x, new_tt, rolling_window):
    """Update rolling mean using new rolling_window value."""
    _update_line(plot, "rolling-mean", new_x, new_tt.rolling(rolling_window, min_periods=1).mean())


def _update_mean(plot, new_x, new_y):
    """Update the new_y mean line."""
    _update_line(plot, "mean", new_x, _hline(new_y.mean(), new_x))


def update(plot, tt_data, date_range, complexity_type, project, rolling_window):
    """Updates a plot from global tt_data."""
    date_range = DateRange(_date_from_js(date_range[0]), _date_from_js(date_range[1]))
    pkg_filter = tt_subset(tt_data, complexity_type, date_range)
    if project is not 'All':
        pkg_filter = pkg_filter & (tt_data['Project'] == project)

    this_complexity = tt_data[pkg_filter]
    new_x = this_complexity['x']
    new_tt = this_complexity['y']

    plot.select_one("datapoints").data_source.data = ColumnDataSource.from_df(this_complexity)
    _update_line(plot, "planned", new_x, this_complexity['planned_y'])
    _update_mean(plot, new_x, new_tt)
    _update_rolling_window(plot, new_x, new_tt, rolling_window)
