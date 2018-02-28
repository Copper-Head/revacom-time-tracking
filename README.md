# Revacom Packaging Performance
This system consists of two components:

- A script that scrapes data from TT (can be run as a cronjob).
- A server that displays plots generated from the scraped data.

## Prerequisites

- [`docker`](https://docs.docker.com/engine/installation/) version 17.06+
- [`docker-compose`](https://docs.docker.com/compose/install/) version 0.15+
- some familiarity with these tools
- Ubuntu host OS
- `/srv/data` folder, where the scraped data will be stored
- `/srv/secrets` folder on your host, where you need to place the credentials to Time Tracker

Here's an example of the expected format for the credentials.
```
{
  "username": "j.doe",
  "password": "supercalifragilisticexpialidocious"
}
```
## Setup from scratch
Run:
```
./from_scratch.sh
```
It will
- install `docker` and `docker-compose`
- scrape the TT website
- start the bokeh server

## The Scraper
To scrape some data from the TT website again, run this command:
```
./scraper.sh
```
This will make several requests to TT, scrape the response and place a CSV file in `/srv/data`.

### Caching
So as not to pull old data unnecessarily the scraper caches the date spans for which it already requested a report.
This cache is stored in a simple text file and which can be easily removed/renamed to invalidate it.
Removing/renaming the output CSV file also busts the cache.


## Bokeh Server
Once you collect the data with the scraper, it's time to visualize it!
The code for the server can be found in the `app` folder.

### Running the Server
For the first time, deploy with this command:
```
docker-compose up -d
```
When re-deploying, use this command:
```
docker-compose up -d --force-recreate --build
```
You can leave out the `--build` flag if you didn't make any changes to the server code and are just deploying a new docker container configuration.
You can edit this configuration by simply changing the `docker-compose.yaml` file.

**Note**

If for some reason the CSV file with the data has to be recreated, you will need to re-deploy the app!

### Assumptions
When generating the plots we made some assumptions about our data.
You can find (and tweak) all of them in `app/assumptions.py`
