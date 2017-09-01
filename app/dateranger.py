"""Handling date ranges consistently."""
from collections import namedtuple
from datetime import date, datetime

from bokeh.io import curdoc

DATE_FORMAT = "%d/%m/%Y"

DateRange = namedtuple("DateRange", "start end")


def _date_from_str(date: str, default: datetime.date) -> datetime.date:
    try:
        return datetime.strptime(date, DATE_FORMAT).date()
    except ValueError:
        return default


def _extract(request_arguments: dict, arg_name: str) -> str:
    value = request_arguments.get(arg_name, [])
    return value[0].decode() if value else ""


def _extract_start_end(request_arguments: dict) -> tuple:
    return _extract(request_arguments, "start"), _extract(request_arguments, "end")


def date_range_from_request(default_start, default_end) -> tuple:
    """Infer date range selection from request."""
    request_args = curdoc().session_context.request.arguments
    start, end = _extract_start_end(request_args)
    return DateRange(_date_from_str(start, default_start), _date_from_str(end, default_end))


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


def date_range_from_js(date_range: tuple):
    return DateRange(_date_from_js(date_range[0]), _date_from_js(date_range[1]))
