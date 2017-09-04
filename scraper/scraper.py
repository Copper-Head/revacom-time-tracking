"""Provides code to scrape tt.revacom.com and process results into a CSV file."""
import csv
import logging
from datetime import date, datetime
import os
import json
from calendar import Calendar
from collections import namedtuple
from itertools import chain, takewhile
from functools import partial

import requests
from bs4 import BeautifulSoup

logging.basicConfig(format="%(asctime)s -- %(levelname)s -- %(message)s")

ROOT_URL = "http://tt.revacom.com"
LOGIN_URL = ROOT_URL + "/Home/Login"
LINK_TPL = (ROOT_URL + "/GetAssignment/PackagingStatistic?group_type=proj&proj=&isWeek=false"
            "&from={0}&to={1}&account=132&date_type=month&all_proj=true"
            "&fromweek=&toweek=&refresh_report=false")
CACHE_TPL = "{0}\t{1}"
# Less conventional (but URL-friedly) date format
LINK_DATE_FMT = "%Y-%m"
# Date format used for chache entries and saved to CSV.
# It's automatically parsed by pandas.
DATE_FMT = "%Y-%m-%d"
CACHE_PATH = "/data/scrape-dates-cache"
OUTPUT_FILE = "/data/time_tracking.csv"

Span = namedtuple("Span", "start end")


def week_to_span(calendar_week: list):
    return Span(calendar_week[0], calendar_week[-1])


def span_to_str(span: Span):
    return (span.start.strftime(DATE_FMT), span.end.strftime(DATE_FMT))


def strings_to_span(start: str, end: str):
    return Span(datetime.strptime(start, DATE_FMT).date(), datetime.strptime(end, DATE_FMT).date())


def insert_span_str(template: str, span: Span):
    return template.format(*span_to_str(span))


def span_to_url(span: Span):
    return insert_span_str(LINK_TPL, span)


def span_to_cache_entry(span: Span):
    return insert_span_str(CACHE_TPL, span)


def cache_entry_to_span(line: str):
    return strings_to_span(*line.split())


def cache_file():
    """Opens file in append or write mode depending on whether it's already present."""
    mode = 'w'
    if os.path.isfile(CACHE_PATH):
        mode = 'a'
    return open(CACHE_PATH, mode)


def clear_cache():
    """Removes cache file if present."""
    try:
        os.remove(CACHE_PATH)
    except OSError:
        pass


def instantiate_span_cache():
    """Read cache file (if present) into memory."""
    if not os.path.isfile(CACHE_PATH):
        return set()

    with open(CACHE_PATH) as cache_f:
        return set(cache_entry_to_span(line) for line in cache_f)


def all_weeks(start_date, end_date):
    """Chain together calendar weeks from start date to end date."""
    # Our calendar's first/last week day is a Sunday!
    cal = Calendar(firstweekday=6)
    return chain.from_iterable(
        chain.from_iterable(
            chain.from_iterable(
                cal.yeardatescalendar(year) for year in range(start_date.year, end_date.year + 1))))


def week_is_before(some_date: date, week):
    """Check if last day of week happened before some date."""
    return week[-1] < some_date


def generate_spans(cache, start_date=None, end_date=None):
    """Lazily generates spans of one week each from start_date to end_date."""
    start_date = date(2012, 1, 1) if start_date is None else start_date
    end_date = date.today() if end_date is None else end_date

    up_to_today = takewhile(partial(week_is_before, end_date), all_weeks(start_date, end_date))
    return filter(lambda span: span not in cache, map(week_to_span, up_to_today))



def request_report(report_link: str, login_payload: dict):
    """Login and request a report.

    Given how long it takes TimeTracker to respond to requests for reports,
    it makes sense to login separately for each request.
    """
    with requests.Session() as session:
        session.post(LOGIN_URL, data=login_payload)
        logging.debug("Done authenticating")
        # wait forever with timeout=None
        return session.get(report_link, timeout=None)


def extract_table(report_page: requests.Response):
    """Extract list of rows (table) from the report HTML page."""
    soup = BeautifulSoup(report_page.content, 'html.parser')
    table = soup.find(id='issueDetails')
    # first entry is the period for which we're searching
    if table:
        logging.debug("found the table")
        rows = filter(None, (tr('td') for tr in iter(table('tr'))))
        return [[td.string for td in tr] for tr in rows]
    return []


def split_jira_key(table_row):
    # this is admittedly wonky, to rely on the jira key's position in the row to stay consistent
    return table_row[:1] + table_row[0].split('-') + table_row[1:]


def scrape_to_csv():
    """Main module function.

    Either creates a new CSV file or updates an existing one with the
    data scraped from tt.revacom.com

    To avoid requesting and processing entries twice, caches them.
    """
    with open("/secrets/tt_credentials.json") as f:
        LOGIN_CREDENTIALS = json.load(f)
    # If the output file doesn't exist, we should recreate it from scratch.
    if not os.path.isfile(OUTPUT_FILE):
        # Here's the code for extracting header:
        # [" ".join(c for c in th.children if isinstance(c, str)) for th in table.tr.children]
        # Prepend "Date" to this and you have the full header
        # yapf: disable
        header_row = [
            'Date',
            'JIRA-Key',
            'Project',
            "Package Number",
            'Name',
            'Type',
            'Complexity',
            'Technology',
            'Status',
            'Packager',
            'QA',
            'Account/ Order#',
            'Total Time (1)',
            'Time in period (2)',
            'QA passes',
            'Overdue',
            'Innovations (hr)',
            'Packaging &  Development',
            'Testing (hr)',
            'TR package (hr)'
        ]
        # yapf: enable
        with open(OUTPUT_FILE, 'w') as outfile:
            csvfile = csv.writer(outfile)
            csvfile.writerow(header_row)
        # We aslo want to reset the cache
        clear_cache()

    for timespan in generate_spans(instantiate_span_cache()):
        table_rows = extract_table(
            request_report(span_to_url(timespan), LOGIN_CREDENTIALS))

        table_rows = map(split_jira_key, table_rows)
        rows_with_date = [[timespan.start.strftime(DATE_FMT)] + row for row in table_rows]

        with open(OUTPUT_FILE, 'a', encoding='utf-8') as outf:
            csvfile = csv.writer(outf)
            csvfile.writerows(rows_with_date)

        with cache_file() as cache_f:
            cache_f.write(span_to_cache_entry(timespan))


if __name__ == '__main__':
    scrape_to_csv()
