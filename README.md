# Revacom Time Tracking


## Bokeh Server
This displays the monthly stats for packages.

### Prerequisites

- `docker` version 17.06+
- `docker-compose` version 0.15+
- `/srv/data` folder on your docker host

### Deployment

For the first time, deploy with this command:
```
docker-compose up -d --build
```
When re-deploying, use this command:
```
docker-compose up -d --force-recreate --build
```
You can leave out the `--build` flag if you didn't make any changes to the server code and are just re-deploying a new configuration.

## Running Scraper Job

Trying to support both dockerized and non-dockerized setups proved to be trickier than expected,
so for now this only runs in a docker container.

```
docker build . -t time-tracking-scraper
```

When you run the container you need to mount two volumes:

- one in `/project` containing `TimeSheetData.ipynb` and `scraper.py` (the easiest is to just mount this repository)
- one under `/data/` where the output will be saved

Here's an example run command assuming there is a `/data` directory on the host.
```
docker run -v /data:/data/ /project:$PWD time-tracking-scraper
```
