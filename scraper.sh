#!/usr/bin/env bash

set -e
docker build -t time-tracking-scraper scraper
docker run -v /srv/data:/data/ -v /srv/secrets:/secrets time-tracking-scraper
