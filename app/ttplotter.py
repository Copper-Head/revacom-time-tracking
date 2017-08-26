"""Houses plot generation and updating logic."""
import numpy as np
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool


def _hline(y_value, x_values):
    """Generates a horizontal line by repeating y_value."""
    return np.repeat(y_value, len(x_values))


def generate_plot(data):
    """Create bokeh figure from some initial data."""
    plot = figure(
        x_axis_type="datetime",
        # plot_height=height,
        # plot_width=width,
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


def update(plot, tt_data, complexity_type, project, rolling_window):
    """Updates a plot from global tt_data."""
    pkg_filter = (tt_data['Complexity'] == complexity_type)
    if project is not 'All':
        pkg_filter = pkg_filter & (tt_data['Project'] == project)

    this_complexity = tt_data[pkg_filter]
    new_x = this_complexity['x']
    new_tt = this_complexity['y']

    plot.select_one("datapoints").data_source.data = ColumnDataSource.from_df(this_complexity)
    _update_line(plot, "planned", new_x, this_complexity['planned_y'])
    _update_mean(plot, new_x, new_tt)
    _update_rolling_window(plot, new_x, new_tt, rolling_window)
