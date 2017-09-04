import datetime

import pytest
from scraper import (Calendar, Span, week_to_span, span_to_str, insert_span_str,
                     cache_entry_to_span)


@pytest.fixture
def test_span():
    return Span(datetime.date(2017, 8, 28), datetime.date(2017, 9, 3))


def test_week_to_span():
    sample_week = Calendar().monthdatescalendar(2017, 9)[0]

    assert week_to_span(sample_week) == Span(datetime.date(2017, 8, 28), datetime.date(2017, 9, 3))


def test_span_to_str(test_span):
    assert span_to_str(test_span) == ("2017-08-28", "2017-09-03")


def test_insert_span_str(test_span):
    template = "Dummy date from {0} to {1}"

    assert insert_span_str(template, test_span) == "Dummy date from 2017-08-28 to 2017-09-03"


def test_cache_entry_to_span(test_span):
    line = "2017-08-28 2017-09-03"
    line2 = "2017-08-28   2017-09-03"
    line3 = "2017-08-28\t2017-09-03"

    assert cache_entry_to_span(line) == test_span
    assert cache_entry_to_span(line2) == test_span
    assert cache_entry_to_span(line3) == test_span


def test_cache_entry_to_span_invalid_inputs():
    with pytest.raises(TypeError):
        cache_entry_to_span("")

    with pytest.raises(TypeError):
        cache_entry_to_span("2017-08-28\t2017-09-03\t017-09-03")
