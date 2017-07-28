"""Provides code to scrape tt.revacom.com and process results into a CSV file."""
import csv
import logging
from datetime import date, datetime
import os
import json

import requests
from bs4 import BeautifulSoup

logfile = 'scrape_log'
logging.basicConfig(
    filename=logfile,
    filemode='w',
    level=logging.DEBUG,
    format="%(asctime)s -- %(levelname)s -- %(message)s")

ROOT_URL = "http://tt.revacom.com"
LOGIN_URL = ROOT_URL + "/Home/Login"
LINK_TPL = (ROOT_URL + "/GetAssignment/PackagingStatistic?group_type=proj&proj=&isWeek=false"
            "&from={start_ym}-01&to={end_ym}-01&account=132&date_type=month&all_proj=true"
            "&fromweek=&toweek=&refresh_report=false")
# Less conventional (but URL-friedly) date format
LINK_DATE_FMT = "%Y-%m"
# Date format used for chache entries and saved to CSV.
# It's automatically parsed by pandas.
DATE_FMT = "%Y/%m"
CACHE_PATH = "/data/scrape-dates-cache"
OUTPUT_FILE = "/data/time_tracking.csv"
with open("/data/tt_credentials.json") as f:
    LOGIN_CREDENTIALS = json.load(f)


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
        return set(_cache_entry_to_span_tuple(line.strip()) for line in cache_f)


def _cache_entry_to_span_tuple(cache_entry):
    """Turn cache date span entry into tuple of start and end date."""
    start, end = cache_entry.split('-')
    start_date = datetime.strptime(start, DATE_FMT)
    end_date = datetime.strptime(end, DATE_FMT)
    return start_date, end_date


def _span_to_cache_entry(start_date, end_date):
    """Turn start and end date into string to save in the cache file."""
    return "{0}-{1}\n".format(start_date.strftime(DATE_FMT), end_date.strftime(DATE_FMT))


def generate_spans(span_cashe, start_date=None, end_date=None):
    """Lazily generates spans of one month from start_date to end_date."""
    if start_date is None:
        start_date = date(2012, 1, 1)
    if end_date is None:
        end_date = date.today()

    for year in range(start_date.year, end_date.year + 1):
        n_months = 12 if year != end_date.year else end_date.month
        for month in range(1, n_months + 1):
            dec = month == 12
            year2 = year if not dec else year + 1
            month2 = month + 1 if not dec else 1

            report_span = (date(year, month, 1), date(year2, month2, 1))
            if report_span not in span_cashe:
                yield report_span


def span_to_url(start_date, end_date):
    """Interpolates start and end dates into URL."""
    # yapf: disable
    return LINK_TPL.format(
        start_ym=start_date.strftime(LINK_DATE_FMT),
        end_ym=end_date.strftime(LINK_DATE_FMT))
    # yapf: enable


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


def scrape_to_csv():
    """Main module function.

    Either creates a new CSV file or updates an existing one with the
    data scraped from tt.revacom.com

    To avoid requesting and processing entries twice, caches them.
    """
    # If the output file doesn't exist, we should recreate it from scratch.
    if not os.path.isfile(OUTPUT_FILE):
        # Here's the code for extracting header:
        # [" ".join(c for c in th.children if isinstance(c, str)) for th in table.tr.children]
        # Prepend "Date" to this and you have the full header
        # yapf: disable
        header_row = [
            'Date',
            'JIRA-Key',
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

    for start_date, end_date in generate_spans(instantiate_span_cache()):
        table_rows = extract_table(
            request_report(span_to_url(start_date, end_date), LOGIN_CREDENTIALS))

        rows_with_date = [[start_date.strftime(DATE_FMT)] + row for row in table_rows]

        with open(OUTPUT_FILE, 'a', encoding='utf-8') as outf:
            csvfile = csv.writer(outf)
            csvfile.writerows(rows_with_date)

        with cache_file() as cache_f:
            cache_f.write(_span_to_cache_entry(start_date, end_date))


if __name__ == '__main__':
    scrape_to_csv()
