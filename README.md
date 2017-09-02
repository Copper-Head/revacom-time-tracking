# Revacom Time Tracking


## Bokeh Server
This displays basic monthly performance stats for packages listed in Time Tracker.
The code can be found in the `app` folder.

### Prerequisites

- `docker` version 17.06+
- `docker-compose` version 0.15+
- some familiarity with these tools
- `/srv/data` folder on your docker host

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
Trying to support both dockerized and non-dockerized setups proved to be trickier than expected,
so for now this only runs in a docker container.
```
docker build -t time-tracking-scraper scraper
```
When you run the container you need to mount two volumes:

- one in `/project` containing `TimeSheetData.ipynb` and `scraper.py` (the easiest is to just mount this repository)
- one under `/data/` where the output will be saved

Here's an example run command assuming there is an `/srv/data` directory on the host.
```
docker run -v /srv/data:/data/ /project:$PWD time-tracking-scraper
```
