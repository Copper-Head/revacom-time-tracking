"""Houses plot generation and updating logic."""
import numpy as np
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool

from datawrangler import tt_subset, planned_col_name
from dateranger import date_range_from_js


def _hline(y_value, x_values):
    """Generates a horizontal line by repeating y_value."""
    return np.repeat(y_value, len(x_values))


def generate_plot(data, metric_name):
    """Create bokeh figure from some initial data."""
    Metric_Name = metric_name.title()
    plot = figure(
        x_axis_type="datetime",
        plot_width=900,
        active_scroll='wheel_zoom',
        title="Package {}".format(Metric_Name),
        x_axis_label='Time',
        y_axis_label='{} (EUR)'.format(Metric_Name),
        title_location='above',
        name=metric_name)

    plot.add_tools(HoverTool(tooltips=[("Project", "@Project"), ('Package Number', '@Pkg_ID')]))

    data = data.rename(columns={metric_name: 'y'})
    xs = data['x']
    tt = data['y']

    plot.scatter(
        'x', 'y', name='datapoints', source=ColumnDataSource.from_df(data), legend=Metric_Name)

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
        _hline(np.nan, xs),
        line_color='green',
        name='planned',
        legend='Planned {}'.format(Metric_Name),
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
    """Updates a plot from tt_data."""
    pkg_filter = tt_subset(tt_data, complexity_type, date_range_from_js(date_range))
    if project is not 'All':
        pkg_filter = pkg_filter & (tt_data['Project'] == project)

    metric_name = plot.name
    this_complexity = tt_data[pkg_filter].rename(columns={metric_name: 'y'})
    new_x = this_complexity['x']
    new_tt = this_complexity['y']

    plot.select_one("datapoints").data_source.data = ColumnDataSource.from_df(this_complexity)
    if complexity_type == 'All':
        planned_measure = _hline(np.nan, new_x)
    else:
        planned_measure = this_complexity[planned_col_name(metric_name)]
    _update_line(plot, "planned", new_x, planned_measure)
    _update_mean(plot, new_x, new_tt)
    _update_rolling_window(plot, new_x, new_tt, rolling_window)
