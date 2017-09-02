# Revacom Time Tracking


## Bokeh Server
This displays basic monthly performance stats for packages listed in Time Tracker.
The code can be found in the `app` folder.

### Prerequisites

- `docker` version 17.06+
- `docker-compose` version 0.15+
- some familiarity with these tools
- `/srv/data` folder on your docker host, where the scraped data will be stored
- `/srv/secrets` folder on your host, where the credentials to TT need to be placed

### Deployment
For the first time, deploy with this command:
```
docker-compose up -d
```
This will reference the `docker-compose.yaml` to determine which container images to build or pull and which volumes to create.

When re-deploying, use this command:
```
docker-compose up -d --force-recreate --build
```
You can leave out the `--build` flag if you didn't make any changes to the server code and are just deploying a new docker container configuration.
You can edit this configuration by simply changing the `docker-compose.yaml` file.

### Assumptions
When generating the plots we made some assumptions about our data.
You can find (and tweak) all of them in `app/assumptions.py`

## Running Scraper Job
To build the docker container image, run this command:
```
docker build -t time-tracking-scraper scraper
```
Before you run this container, make sure to store your username and password for TT in a JSON file `tt_credentials.json` in the `/srv/secrets` folder.
Here's an example of the expected format.
```
{
  "username": "j.doe",
  "password": "supercalifragilisticexpialidocious"
}
```
With this taken care of, feel free to run the container:
```
docker run -v /srv/data:/data/ -v /srv/secrets:/secrets time-tracking-scraper
```
This will make several requests to TT, scrape the response and place a CSV file in `/srv/data`.
